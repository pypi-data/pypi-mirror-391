from __future__ import annotations

from datetime import timedelta
from difflib import SequenceMatcher
from typing import List, Optional, Tuple
import re

from pydantic import ValidationError

from .cache import DEFAULT_TTLS, JsonCache
from .client import BlackboardClient
from .config import get_settings
from .models import Announcement, CalendarItem, Course, Folder, GradedItem


class CourseLookupError(ValueError):
    def __init__(self, query: str, suggestions: List[Course]):
        self.query = query
        self.suggestions = suggestions
        suggestion_text = ", ".join(f"{course.code} ({course.title})" for course in suggestions[:3])
        message = f"Course '{query}' not found."
        if suggestion_text:
            message += f" Did you mean: {suggestion_text}?"
        super().__init__(message)


class BlackboardService:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = BlackboardClient(settings.bb_username, settings.bb_password, settings.bb_base_url)
        self._cache = JsonCache(settings.cache_file)

    async def close(self) -> None:
        await self._client.aclose()

    async def get_courses(self, force_refresh: bool = False) -> List[Course]:
        return await self._get_cached_list(
            key="courses",
            loader=self._client.fetch_courses,
            model=Course,
            ttl=DEFAULT_TTLS["courses"],
            force_refresh=force_refresh,
        )

    async def get_announcements(self, course_code: str, limit: Optional[int] = None) -> List[Announcement]:
        course = await self._require_course(course_code)
        cache_key = f"announcements:{course.id}"
        announcements = await self._get_cached_list(
            key=cache_key,
            loader=lambda: self._client.fetch_announcements(course),
            model=Announcement,
            ttl=DEFAULT_TTLS["announcements"],
        )
        if limit is not None:
            return announcements[:limit]
        return announcements

    async def get_grades(self, course_code: str) -> List[GradedItem]:
        course = await self._require_course(course_code)
        cache_key = f"grades:{course.id}"
        return await self._get_cached_list(
            key=cache_key,
            loader=lambda: self._client.fetch_grades(course),
            model=GradedItem,
            ttl=DEFAULT_TTLS["grades"],
        )

    async def get_calendar(self) -> List[CalendarItem]:
        return await self._get_cached_list(
            key="todo",
            loader=self._client.fetch_calendar,
            model=CalendarItem,
            ttl=DEFAULT_TTLS["todo"],
        )

    async def get_content_tree(self, course_code: str) -> Folder:
        course = await self._require_course(course_code)
        cache_key = f"content_tree:{course.id}"
        entry = await self._cache.read(cache_key)
        if entry and not entry.expired:
            try:
                return Folder.model_validate(entry.payload)
            except ValidationError:
                await self._cache.clear(cache_key)
        folder = await self._client.fetch_content_tree(course)
        await self._cache.write(cache_key, folder.model_dump(mode="json"), DEFAULT_TTLS["content_tree"])
        return folder

    # async def find_content(self, course_code: str, folder_name: str, content_name: str):
    #     root = await self.get_content_tree(course_code)
    #     target = _normalize_keyword(content_name)
    #     search_scope: Optional[Folder] = None
    #     # 优先在指定文件夹内搜索；若找不到该文件夹，则在整棵树回退搜索
    #     if folder_name and folder_name.strip():
    #         search_scope = _locate_folder(root, folder_name)
    #     if search_scope is None:
    #         search_scope = root
    #     return _search_in_folder(search_scope, target)

    async def search_in_folder(self, course_code: str, folder_name: str, keyword: str):
        """
        仅在“指定文件夹”内进行递归搜索，返回所有命中项；若找不到该文件夹则返回空列表。
        不会回退到整棵树。
        """
        root = await self.get_content_tree(course_code)
        if not folder_name or not folder_name.strip():
            return []
        folder = _locate_folder(root, folder_name)
        if folder is None:
            return []
        target = _normalize_keyword(keyword)
        return _search_all_in_folder(folder, target)

    async def download_file(self, url: str, name: str):
        data, extension = await self._client.download_file(url, name)
        return data, extension

    async def _get_cached_list(self, key: str, loader, model, ttl: timedelta, force_refresh: bool = False):
        if not force_refresh:
            entry = await self._cache.read(key)
            if entry and not entry.expired:
                try:
                    return [model.model_validate(item) for item in entry.payload]
                except ValidationError:
                    await self._cache.clear(key)
        data = await loader()
        await self._cache.write(key, [item.model_dump(mode="json") for item in data], ttl)
        return data

    async def _require_course(self, code: str) -> Course:
        course, suggestions = await self._resolve_course(code)
        if course is None:
            raise CourseLookupError(code, suggestions)
        return course

    async def _resolve_course(self, code: str) -> Tuple[Optional[Course], List[Course]]:
        courses = await self.get_courses()
        if not courses:
            return None, []

        query = code.strip()
        normalized = query.lower()

        for course in courses:
            if normalized == course.code.lower() or normalized == course.id.lower():
                return course, []

        substring_matches = [
            course for course in courses
            if normalized and (
                normalized in course.code.lower()
                or normalized in course.id.lower()
                or normalized in course.title.lower()
            )
        ]
        if len(substring_matches) == 1:
            return substring_matches[0], []

        suggestions = self._suggest_courses(courses, normalized)
        return None, suggestions

    def _suggest_courses(self, courses: List[Course], normalized_query: str) -> List[Course]:
        if not courses:
            return []
        scored: List[Tuple[float, Course]] = []
        for course in courses:
            code = course.code.lower()
            course_id = course.id.lower()
            title = course.title.lower()
            score = 0.0
            if normalized_query:
                if (
                    normalized_query in code
                    or normalized_query in course_id
                    or normalized_query in title
                ):
                    score = 1.0
                else:
                    score = max(
                        SequenceMatcher(None, normalized_query, code).ratio(),
                        SequenceMatcher(None, normalized_query, course_id).ratio(),
                        SequenceMatcher(None, normalized_query, title).ratio(),
                    )
            scored.append((score, course))

        scored.sort(key=lambda item: item[0], reverse=True)
        suggestions = [course for score, course in scored if score > 0.3][:3]
        if not suggestions:
            suggestions = [course for _, course in scored[:3]]
        return suggestions


def render_course_summary(course: Course) -> str:
    return (
        f"Title: {course.title}\n"
        f"Code: {course.code}\n"
        f"Instructor: {course.instructor}\n"
        f"ID: {course.id}"
    )


def render_announcement(announcement: Announcement) -> str:
    time_part = announcement.time.isoformat() if announcement.time else "Unknown"
    detail = announcement.detail or "No detail provided."
    return (
        f"Title: {announcement.title}\n"
        f"Poster: {announcement.poster}\n"
        f"Time: {time_part}\n"
        f"Detail: {detail}"
    )


def render_grade(grade: GradedItem) -> str:
    date = grade.date.isoformat() if grade.date else "Unknown"
    return (
        f"Title: {grade.title}\n"
        f"Grade: {grade.grade or 'Unknown'}\n"
        f"Max Point possible: {grade.max_grade or 'Unknown'}\n"
        f"Average: {grade.average or 'Unknown'}\n"
        f"Median: {grade.median or 'Unknown'}\n"
        f"Date: {date}"
    )


def render_todo(calendar: CalendarItem) -> str:
    return (
        f"Summary: {calendar.summary or 'Unknown'}\n"
        f"Link: {calendar.link or 'Unknown'}\n"
        f"Start: {calendar.dtstart.isoformat() if calendar.dtstart else 'Unknown'}\n"
        f"End: {calendar.dtend.isoformat() if calendar.dtend else 'Unknown'}"
    )


def render_content_tree(folder: Folder) -> str:
    lines: List[str] = []

    def walk(current: Folder, prefix: str = "", is_last: bool = True) -> None:
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{current.name}")
        next_prefix = f"{prefix}{'    ' if is_last else '│   '}"
        for index, node in enumerate(current.contents):
            last = index == len(current.contents) - 1
            if isinstance(node, Folder):
                walk(node, next_prefix, last)
            else:
                label = _content_node_label(node)
                lines.append(f"{next_prefix}{'└── ' if last else '├── '}{label}")

    walk(folder)
    return "\n".join(lines)


def _content_node_label(node) -> str:
    if hasattr(node, "name"):
        return getattr(node, "name")
    if hasattr(node, "title"):
        return getattr(node, "title")
    return "item"


def _locate_folder(root: Folder, name: str) -> Optional[Folder]:
    target = name.strip().lower()
    if root.name.strip().lower() == target:
        return root
    for node in root.contents:
        if isinstance(node, Folder):
            found = _locate_folder(node, name)
            if found:
                return found
    return None


# ----------------------------
# 搜索辅助
# ----------------------------

_SEPARATORS = re.compile(r"[\s._-]+")


def _normalize_keyword(text: str) -> str:
    """标准化关键词：小写 + 去除空白/下划线/连字符/点号"""
    return _SEPARATORS.sub("", text.strip().lower())


def _strip_extension(name: str) -> str:
    return name[: name.rfind(".")] if "." in name else name


def _matches(label: str, target_norm: str) -> bool:
    """
    更宽松的匹配：
    - 忽略大小写、空白、下划线/连字符/点号
    - 支持忽略扩展名
    - 支持子串包含
    - 轻度模糊匹配（阈值0.86）
    """
    label_norm = _normalize_keyword(label)
    label_noext_norm = _normalize_keyword(_strip_extension(label))
    if (
        label_norm == target_norm
        or label_noext_norm == target_norm
        or target_norm in label_norm
        or target_norm in label_noext_norm
    ):
        return True
    # 轻度模糊匹配，容忍少量字符差异（如 Q/0 混淆、漏扩展名等）
    ratio = max(
        SequenceMatcher(None, label_norm, target_norm).ratio(),
        SequenceMatcher(None, label_noext_norm, target_norm).ratio(),
    )
    return ratio >= 0.86


# def _search_in_folder(folder: Folder, target_norm: str):
#     """
#     递归搜索：
#     - 遍历当前文件夹的所有直接子节点
#     - 命中则返回该节点
#     - 若为 Folder，继续递归
#     - 若为 Item，进入其附件列表匹配
#     """
#     from .models import Item, File, Link, Assignment  # 延迟导入，避免循环

#     for node in folder.contents:
#         label = _content_node_label(node)
#         if label and _matches(label, target_norm):
#             return node

#         # Item 的附件
#         if isinstance(node, Item):
#             for att in node.attachment:
#                 if _matches(att.name, target_norm):
#                     return att

#         # 继续递归 Folder
#         if isinstance(node, Folder):
#             found = _search_in_folder(node, target_norm)
#             if found:
#                 return found

#     return None


def _search_all_in_folder(folder: Folder, target_norm: str):
    """
    仅在给定文件夹子树内，收集“所有”匹配的节点并返回列表。
    - 匹配规则与 _search_in_folder 相同（宽松匹配 + Item 附件名）。
    - 不向父级或其它分支回退。
    """
    from .models import Item, Folder as FolderModel  # 避免循环导入

    results = []

    def walk(current: Folder):
        for node in current.contents:
            label = _content_node_label(node)
            if label and _matches(label, target_norm):
                results.append(node)
            if isinstance(node, Item):
                for att in node.attachment:
                    if _matches(att.name, target_norm):
                        results.append(att)
            if isinstance(node, FolderModel):
                walk(node)

    walk(folder)
    return results
