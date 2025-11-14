from typing import Optional, Type, Dict
from rest_framework.serializers import BaseSerializer


class ReadWriteSerializerMixin:
    """
    Choose read/write serializers with optional per-action overrides.

    Resolution order:
      - If called with `data=...`  -> write serializer for action (if any) else default write else default read.
      - If called with `instance=...` -> read serializer for action (if any) else default read else default write.
      - If neither `data` nor `instance` provided:
          * if action is known -> prefer read serializer for action (fallback to defaults)
          * else -> default read (fallback to default write)

    Define in your view:
      read_serializer_class: Type[BaseSerializer]         # default read
      write_serializer_class: Type[BaseSerializer]        # default write
      action_read_serializer_classes: Dict[str, Type[BaseSerializer]]   # optional per-action read
      action_write_serializer_classes: Dict[str, Type[BaseSerializer]]  # optional per-action write
    """

    # Defaults (override in subclasses)
    read_serializer_class: Optional[Type[BaseSerializer]] = None
    write_serializer_class: Optional[Type[BaseSerializer]] = None

    # Per-action overrides (override in subclasses)
    action_read_serializer_classes: Optional[Dict[str, Type[BaseSerializer]]] = None
    action_write_serializer_classes: Optional[Dict[str, Type[BaseSerializer]]] = None

    # ------- helpers ---------------------------------------------------------
    def _default_read_cls(self) -> Type[BaseSerializer]:
        """
        Default read serializer. Falls back to `serializer_class` if not set.
        """
        cls = self.read_serializer_class or getattr(self, "serializer_class", None)
        if cls is None:
            raise AssertionError(
                "Read serializer is not configured. "
                "Set `read_serializer_class` or `serializer_class` on the view."
            )
        return cls

    def _default_write_cls(self) -> Type[BaseSerializer]:
        """
        Default write serializer. Falls back to default read if not set.
        """
        return self.write_serializer_class or self._default_read_cls()

    def _action_read_cls(self, action: Optional[str]) -> Optional[Type[BaseSerializer]]:
        if not action or not self.action_read_serializer_classes:
            return None
        return self.action_read_serializer_classes.get(action)

    def _action_write_cls(self, action: Optional[str]) -> Optional[Type[BaseSerializer]]:
        if not action or not self.action_write_serializer_classes:
            return None
        return self.action_write_serializer_classes.get(action)

    # ------- main hook -------------------------------------------------------
    def get_serializer(self, *args, **kwargs) -> BaseSerializer:
        """
        DRF calls this for both validation (data=...) and response (instance=...).
        We pick the appropriate serializer according to the rules above.
        """
        kwargs.setdefault("context", self.get_serializer_context())
        action = getattr(self, "action", None)

        if "data" in kwargs:
            # Write path
            serializer_class = self._action_write_cls(action) or self._default_write_cls()
        elif "instance" in kwargs:
            # Read path
            serializer_class = self._action_read_cls(action) or self._default_read_cls()
        else:
            # Indeterminate; prefer read for that action, then fall back
            serializer_class = (
                self._action_read_cls(action)
                or self._default_read_cls()
            )

        return serializer_class(*args, **kwargs)