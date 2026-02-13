from ..tenant_context import TenantContext


class DynamicDatabaseAlias(str):
    def __new__(cls):
        # We initialize with a dummy value; the logic happens in the methods below
        return super().__new__(cls, "default")

    def __getattribute__(self, name):
        return getattr(TenantContext.get(), name)

    def __str__(self):
        return TenantContext.get()

    def __repr__(self):
        return repr(self.__str__())

    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, other):
        return self.__str__() == str(other)
