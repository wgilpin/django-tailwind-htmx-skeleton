from pytest_factoryboy import register

import factories

register(factories.UserFactory)
register(factories.NoteFactory)
