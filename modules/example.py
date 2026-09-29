from core.module import K9Module


class ExampleModule(K9Module):
    name = "example"

    def run(self, context):
        return {
            "module": self.name,
            "status": "ok",
            "message": "Example module executed.",
        }
