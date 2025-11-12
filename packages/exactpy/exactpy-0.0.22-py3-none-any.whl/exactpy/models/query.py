from typing import Any, Dict, Iterable, List, Tuple

from pydantic import BaseModel, computed_field

from exactpy.types import FilterOperatorEnum, OrderByDirectionEnum


class OrderByModel(BaseModel):
    key: str
    direction: OrderByDirectionEnum


class FilterModel(BaseModel):
    key: str
    val: int | float | str | List[int | float | str] | Tuple[int | float | str]
    op: FilterOperatorEnum
    meta: Dict[str, Any] = {}

    @computed_field
    @property
    def str_value(self) -> str:
        op = str(self.op)
        basic_ops = ("eq", "ne", "lt", "le", "gt", "ge")

        if op in basic_ops:
            qu = (
                ""
                if (isinstance(self.val, str) and self.val.lower() in ("true", "false"))
                or isinstance(self.val, int)
                else "'"
            )
            return f"{self.key} {op} {qu}{self.val}{qu}"

        elif op == "range":
            if (
                not isinstance(self.val, Iterable)
                or not len(self.val) == 2
                or not all(isinstance(v, int) or isinstance(v, float) for v in self.val)
            ):
                raise ValueError(
                    "If op is 'range', an iterable with two elements of type float or int should be passed."
                )

            return f"{self.key} ge {self.val} and {self.key} ge {self.val}"

        elif op == "isin":
            if not isinstance(self.val, Iterable):
                raise ValueError("If op is 'isin', an iterable should be passed.")

            vals = ""
            for v in self.val:
                qu = (
                    ""
                    if (
                        isinstance(self.val, str)
                        and self.val.lower() in ("true", "false")
                    )
                    or isinstance(self.val, int)
                    else "'"
                )
                vals.append(f"{qu}{v}{qu}")

            return f"{self.key} in ({','.join(vals)})"

        elif op == "contains":
            if not isinstance(self.val, str):
                raise ValueError("If op is 'contains', a string should be passed.")

            return f"contains({self.key}, '{self.val}')"

        elif op == "startswith":
            if not isinstance(self.val, str):
                raise ValueError("If op is 'startswith', a string should be passed.")

            return f"startswith({self.key}, '{self.val}')"

        elif op == "endswith":
            if not isinstance(self.val, str):
                raise ValueError("If op is 'endswith', a string should be passed.")

            return f"endswith({self.key}, '{self.val}')"

        elif op == "substr":
            if not isinstance(self.val, str):
                raise ValueError("If op is 'substr', a string should be passed.")
            if self.meta is None or not isinstance(self.meta.get("length"), int):
                raise ValueError(
                    "If op is 'substr', a meta data dict with a length: int kv pair should be passed."
                )

            return f"substring({self.key}, {self.meta.get('length')}) eq '{self.val}'"

        elif op == "tolower":
            if not isinstance(self.val, str):
                raise ValueError("If op is 'tolower', a string should be passed.")

            return f"tolower({self.key}) eq '{self.val}')"

        elif op == "toupper":
            if not isinstance(self.val, str):
                raise ValueError("If op is 'v', a string should be passed.")

            return f"toupper({self.key}) eq '{self.val}')"
