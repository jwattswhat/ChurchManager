"""Consistent creation of ChurchManager forms."""


class ChurchManagerFormFactory:
    def __init__(self, form_class, connection, default_parent=None,
                 authorization_policy=None, audit_hook=None):
        self.form_class = form_class
        self.connection = connection
        self.default_parent = default_parent
        self.authorization_policy = authorization_policy
        self.audit_hook = audit_hook

    def create(self, form_name, controls=None, parent=None):
        parent = self.default_parent if parent is None else parent
        keyword_arguments = {}
        if self.authorization_policy is not None:
            keyword_arguments["authorization_policy"] = self.authorization_policy
        if self.audit_hook is not None:
            keyword_arguments["audit_hook"] = self.audit_hook
        if controls is None:
            return self.form_class(parent, self.connection, form_name, **keyword_arguments)
        return self.form_class(
            parent, self.connection, form_name, controls, **keyword_arguments
        )

    def open(self, form_name, controls=None, parent=None):
        form = self.create(form_name, controls, parent)
        form.show()
        return form
