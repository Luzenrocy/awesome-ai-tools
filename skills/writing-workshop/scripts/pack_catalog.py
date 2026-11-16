"""Read the constrained built-in prompt-pack YAML catalogues without dependencies."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path


PACK_START = re.compile(r"^  - id: ([a-z0-9][a-z0-9._-]+)$")
FIELD = re.compile(r"^    ([a-z_]+): (.*)$")


DOCUMENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "technical.architecture": ("架构", "技术方案", "rfc", "系统设计", "接口设计", "architecture"),
    "technical.api-doc": ("api", "sdk", "接口文档", "openapi", "开发者文档"),
    "technical.runbook": ("runbook", "运维", "故障", "sop", "应急", "操作手册"),
    "technical.test-plan": ("测试", "验收", "test plan", "测试计划"),
    "product.prd": ("prd", "需求文档", "产品需求", "用户故事", "功能需求"),
    "product.prototype-brief": ("原型", "交互", "页面", "prototype", "ux"),
    "business.proposal": ("立项", "商业方案", "提案", "商业计划", "汇报"),
    "work.meeting-notes": ("会议纪要", "会议记录", "决策记录"),
    "work.status-report": ("日报", "周报", "月报", "工作汇报", "status report"),
    "content.wechat-article": ("公众号", "微信文章", "长文", "专栏"),
    "content.xiaohongshu": ("小红书", "种草", "笔记"),
    "content.douyin-script": ("抖音", "短视频", "口播", "视频脚本"),
    "fiction.flash": ("短篇小说", "微型小说", "短篇"),
    "fiction.web-novel": ("网文", "连载", "长篇小说", "章节"),
    "life.travel-plan": ("旅行", "旅游", "行程", "攻略", "出行"),
}


ROLE_COMBINATIONS: dict[str, tuple[dict[str, str], ...]] = {
    "technical.architecture": (
        {"writer": "architect", "reviewer": "technical-writer", "checker": "architect"},
        {"writer": "architect", "reviewer": "business-analyst", "checker": "architect"},
    ),
    "technical.api-doc": (
        {"writer": "technical-writer", "reviewer": "architect", "checker": "technical-writer"},
    ),
    "technical.runbook": (
        {"writer": "operations-manager", "reviewer": "technical-writer", "checker": "operations-manager"},
    ),
    "technical.test-plan": (
        {"writer": "technical-writer", "reviewer": "architect", "checker": "architect"},
    ),
    "product.prd": (
        {"writer": "product-manager", "reviewer": "product-designer", "checker": "business-analyst"},
        {"writer": "product-manager", "reviewer": "business-analyst", "checker": "product-manager"},
    ),
    "product.prototype-brief": (
        {"writer": "product-designer", "reviewer": "product-manager", "checker": "product-designer"},
    ),
    "business.proposal": (
        {"writer": "business-analyst", "reviewer": "operations-manager", "checker": "business-analyst"},
    ),
    "work.meeting-notes": (
        {"writer": "operations-manager", "reviewer": "business-analyst", "checker": "operations-manager"},
    ),
    "work.status-report": (
        {"writer": "operations-manager", "reviewer": "business-analyst", "checker": "operations-manager"},
    ),
    "content.wechat-article": (
        {"writer": "content-editor", "reviewer": "content-editor", "checker": "content-editor"},
    ),
    "content.xiaohongshu": (
        {"writer": "content-editor", "reviewer": "content-editor", "checker": "content-editor"},
    ),
    "content.douyin-script": (
        {"writer": "screenwriter", "reviewer": "content-editor", "checker": "screenwriter"},
    ),
    "fiction.flash": (
        {"writer": "novelist", "reviewer": "developmental-editor", "checker": "novelist"},
    ),
    "fiction.web-novel": (
        {"writer": "novelist", "reviewer": "developmental-editor", "checker": "novelist"},
    ),
    "life.travel-plan": (
        {"writer": "operations-manager", "reviewer": "business-analyst", "checker": "operations-manager"},
    ),
}


def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value


def load_catalogue(filename: str) -> tuple[Path, dict[str, dict[str, str]]]:
    """Read the intentionally flat pack YAML format used by this skill."""

    path = skill_dir() / "prompt-packs" / filename
    packs: dict[str, dict[str, str]] = {}
    current: dict[str, str] | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        start = PACK_START.match(raw_line)
        if start:
            current = {"id": start.group(1)}
            packs[start.group(1)] = current
            continue
        field = FIELD.match(raw_line)
        if field and current is not None:
            current[field.group(1)] = _unquote(field.group(2))
    return path, packs


def document_catalogue() -> tuple[Path, dict[str, dict[str, str]]]:
    return load_catalogue("documents.yaml")


def role_catalogue() -> tuple[Path, dict[str, dict[str, str]]]:
    return load_catalogue("roles.yaml")


def recommend_documents(brief: str, limit: int = 3) -> list[dict[str, object]]:
    path, packs = document_catalogue()
    lowered = brief.lower()
    ranked: list[tuple[int, str, tuple[str, ...]]] = []
    for pack_id, keywords in DOCUMENT_KEYWORDS.items():
        matches = tuple(keyword for keyword in keywords if keyword.lower() in lowered)
        if matches:
            ranked.append((len(matches), pack_id, matches))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    selected = ranked[:limit]
    if not selected:
        selected = [(0, "custom", ())]
    results: list[dict[str, object]] = []
    for score, pack_id, matches in selected:
        pack = packs.get(pack_id, {})
        results.append(
            {
                "id": pack_id,
                "label": pack.get("label", "Custom document"),
                "confidence": round(min(0.95, 0.45 + score * 0.2), 2) if score else 0.4,
                "reason": "matched: " + ", ".join(matches) if matches else "no strong built-in match; define a custom contract",
                "catalogue": str(path),
            }
        )
    return results


def recommend_role_combinations(document_pack: str) -> list[dict[str, object]]:
    combinations = ROLE_COMBINATIONS.get(document_pack)
    if combinations is None:
        combinations = ({"writer": "technical-writer", "reviewer": "business-analyst", "checker": "technical-writer"},)
    return [
        {
            "id": f"{document_pack}-roles-{index + 1}",
            "roles": roles,
            "reason": f"default role combination for {document_pack}",
        }
        for index, roles in enumerate(combinations[:3])
    ]
