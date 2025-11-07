from app.core.models import MemoryType


class MemoryNamespaceBuilder:
    """
    메모리 네임스페이스를 일관되게 생성하는 팩토리 클래스.

    네임 스페이스를 설정하면, 메모리를 저장하는 langchain BaseStore 내 store 테이블에, prefix 로 설정됩니다.
    해당 네임스페이스를 기반으로 유사도 search index, filtering query를 생성할 수 있습니다.

    네임스페이스 구조: (memory_type, user_id, category)
    - memory_type: "semantic", "episodic", "procedural"
    - user_id: 사용자 ID
    - category
        "tacit-knowledge(암묵지 - 업무 절차 관련)"
        "user-knowledge(사용자 개인만 사용할 지식)"
        "global(에이전트별 공통 매핑될 정보)"
        "{custom_category}" : 사용자 정의 카테고리 (of 메소드를 통해 추가)
    """

    # 카테고리 상수
    TACIT_KNOWLEDGE = "tacit-knowledge"
    USER_KNOWLEDGE = "user-knowledge"
    REQUEST_ONLY = "request-only"
    GLOBAL = "global"

    @staticmethod
    def of(memory_type: str, user_id: str, category: str) -> tuple[str, str, str]:
        """
        사용자 정의 네임스페이스 생성.

        Args:
            memory_type: 메모리 타입 (자유 문자열)
            user_id: 사용자 ID
            category: 카테고리 (자유 문자열)

        Returns:
            (memory_type, user_id, category)
        """
        return memory_type, user_id, category

    @staticmethod
    def for_user(user_id: str | None) -> tuple[str] | tuple[str, str | None, str]:
        return "memories", user_id, MemoryNamespaceBuilder.REQUEST_ONLY

    @staticmethod
    def for_tacit_knowledge(memory_type: MemoryType, user_id: str) -> tuple[str, str, str]:
        """
        암묵지 (Tacit Knowledge) 메모리용 네임스페이스 생성.

        Args:
            memory_type: 메모리 타입 (semantic/episodic/procedural)
            user_id: 사용자 ID

        Returns:
            (memory_type.value, user_id, "tacit-knowledge")
        """
        return memory_type.value, user_id, MemoryNamespaceBuilder.TACIT_KNOWLEDGE

    @staticmethod
    def for_knowledge(memory_type: MemoryType, user_id: str) -> tuple[str, str, str]:
        """
        사용자 업로드 파일 (지식 파일)용 네임스페이스 생성.

        Args:
            memory_type: MemoryType Enum (SEMANTIC/EPISODIC/PROCEDURAL)
            user_id: 사용자 ID

        Returns:
            (memory_type.value, user_id, "user-knowledge")
        """
        return memory_type.value, user_id, MemoryNamespaceBuilder.USER_KNOWLEDGE

    @staticmethod
    def for_semantic_memory(user_id: str) -> tuple[str, str, str]:
        """
        Semantic Memory용 네임스페이스 생성.

        Args:
            user_id: 사용자 ID

        Returns:
            ("semantic", user_id, "user-knowledge")
        """
        return (
            MemoryType.SEMANTIC.value,
            user_id,
            MemoryNamespaceBuilder.USER_KNOWLEDGE,
        )

    @staticmethod
    def for_episodic_memory(user_id: str) -> tuple[str, str, str]:
        """
        Episodic Memory용 네임스페이스 생성.

        Args:
            user_id: 사용자 ID

        Returns:
            ("episodic", user_id, "user-knowledge")
        """
        return (
            MemoryType.EPISODIC.value,
            user_id,
            MemoryNamespaceBuilder.USER_KNOWLEDGE,
        )

    @staticmethod
    def for_procedural_memory(user_id: str) -> tuple[str, str, str]:
        """
        Procedural Memory용 네임스페이스 생성.

        Args:
            user_id: 사용자 ID

        Returns:
            ("procedural", user_id, "user-knowledge")
        """
        return (
            MemoryType.PROCEDURAL.value,
            user_id,
            MemoryNamespaceBuilder.USER_KNOWLEDGE,
        )

    @staticmethod
    def from_parts(*parts: str) -> tuple[str, ...]:
        """
        여러 파트로 네임스페이스 생성 (가변 길이).

        Args:
            *parts: 네임스페이스 구성 요소들

        Returns:
            (part1, part2, ..., partN)

        Example:
            >>> MemoryNamespaceBuilder.from_parts("custom", "user123", "category", "subcategory")
            ("custom", "user123", "category", "subcategory")
        """
        return tuple(parts)
