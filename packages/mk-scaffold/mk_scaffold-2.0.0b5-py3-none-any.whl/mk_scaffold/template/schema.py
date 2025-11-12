# vim: foldmarker=[[,]] foldmethod=marker
import cerberus

# https://docs.python-cerberus.org/en/stable/validation-rules.html
SCHEMA = r"""
---
actions: # [[
  type: list
  default: []
  schema:
    type: dict
    default: {}
    nullable: true
    schema:
      # actions.hidden
      # --------------
      action:
        type: string
        required: True
        allowed: ["move", "remove", "remove-trailing-newline"]

      # actions.dst
      # -----------
      dst:
        type: string
        excludes: ["path"]

      # actions.else
      # ------------
      else:
        type: string
        allowed: ["remove"]

      # actions.if
      # ----------
      if:
        type: [string, boolean]
        required: True

      # actions.order
      # -------------
      order:
        type: integer
        default: 0

      # actions.path
      # ------------
      path:
        type: [string, list]
        excludes: ["dst", "src"]

      # actions.src
      # -----------
      src:
        type: string
        excludes: ["path"]
# ]]

answers: # [[
  type: dict
  default: {}
# ]]

inherit: # [[
  type: list
  default: []
  schema:
    type: dict
    default: {}
    nullable: true

    schema:
      # inherit.branch
      # --------------
      branch:
        type: string
        nullable: True

      # inherit.include
      # ---------------
      include:
        type: string
        required: true

      # inherit.filename
      # ---------------
      filename:
        type: string
        default: "scaffold.yml"
# ]]

jinja2: # [[
  type: dict
  default: {}
  schema:
    # lstrip_blocks
    lstrip_blocks:
      type: boolean
      default: false

    # trim_blocks
    trim_blocks:
      type: boolean
      default: false
# ]]

questions: # [[
  type: list
  default: []
  schema:
    type: dict
    default: {}
    nullable: true
    schema:

      # questions.description
      # ---------------------
      description:
        type: string

      # questions.hidden
      # ----------------
      hidden:
        type: [string, boolean]
        default: false

      # questions.order
      # ----------------
      order:
        type: integer
        default: 0

      # questions.name
      # --------------
      name:
        type: string
        regex: '^\S+$'
        required: true
        minlength: 1

      # questions.order
      # ---------------
      order:
        type: integer
        nullable: True

      # questions.schema
      # ----------------
      schema:
        type: dict
        nullable: true
        coerce: asdict
        check_with: schema_rules
        schema:

          # questions.schema.allowed
          # ------------------------
          allowed:
            type: list
            schema:
              type: [string, integer]

          # questions.schema.default
          # ------------------------
          default:
            type: [string, boolean, integer]

          # questions.schema.nullable
          # -------------------------
          nullable:
            type: boolean
            default: False

          # questions.schema.max_length
          # ---------------------------
          max_length:
            type: integer

          # questions.schema.max_value
          # ---------------------------
          max_value:
            type: integer

          # questions.schema.min_length
          # ---------------------------
          min_length:
            type: integer
            min: 1

          # questions.schema.min_value
          # ---------------------------
          min_value:
            type: integer

          # questions.schema.type
          # ---------------------
          type:
            type: string
            default: "string"
            allowed: ["string", "integer", "boolean"]
# ]]
"""


class LocalValidator(cerberus.Validator):
    def _normalize_coerce_asdict(self, value):
        if value is None:
            return {}
        return value

    def _normalize_coerce_tolist(self, value):
        if isinstance(value, str):
            return [value]
        return value

    def _check_with_schema_rules(self, field, schema):
        pass


#    # TODO: Validations
#    def _check_with_include_minlength(self, field, value):
#        if value is None:
#            self._error(field, "Length of an 'include' path must be non-zero")
#            return
#
#        for include in value:
#            if len(include) == 0:
#                self._error(field, "Length of an 'include' path must be non-zero")
#                return
#
#    def _check_with_schema_rules(self, field, schema):
#        if schema.get("type") in ["boolean", "string"] and any(k in schema for k in ["min", "max"]):
#            self._error(field, 'neither "min" nor "max" can be specified if "type" is either boolean or string')
#            return
#        if schema.get("type") in ["boolean", "integer"] and any(k in schema for k in ["min_length", "max_length"]):
#            # fmt: off
#            self._error(field, 'neither "min_length" nor "max_length" can be specified if "type" is either boolean or integer')
#            return
#            # fmt: on
#        if "allowed" in schema and schema.get("type") == "boolean":
#            self._error(field, '"allowed" can not be specified if "type" is boolean')
#            return
#        if "allowed" in schema and any(k in schema for k in ["min_length", "max_length", "min", "max"]):
#            # fmt: off
#            self._error(field, '"allowed" can not be specified when one of "min_length", "max_length", "min", or "max" is also specified')
#            return
#            # fmt: on
#        if "min" in schema and "max" in schema:
#            if int(schema["min"]) > int(schema["max"]):
#                self._error(field, '"min" must be inferior to "max"')
#                return
#        if "min_length" in schema and "max_length" in schema:
#            if schema["min_length"] > schema["max_length"]:
#                self._error(field, '"min_length" must be inferior to "max_length"')
#                return
#
#    def _check_with_file_rules(self, field, value):
#        if "else" in value and "if" not in value:
#            self._error(field, '"if" required if a "files" element contains an "else"')
#            return
#        if "move" in [value.get("action", ""), value.get("else", "")] and "dest" not in value:
#            self._error(field, '"dest" required if a "files" element contains an "action" or "else"')
#            return
