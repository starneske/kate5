import time

from qube.src.commons.error import ErrorCodes, kate5ServiceError
from qube.src.commons.utils import clean_nonserializable_attributes
from qube.src.models.kate5 import kate5


class kate5Service:
    def __init__(self, context):
        self.auth_context = context

    def find_by_id(self, entity_id):
        # filter with id not working,
        # unable to proceed with tenant filter
        data = kate5.query.get(entity_id)
        if data is None:
            raise kate5ServiceError(
                'kate5 {} not found'.format(entity_id),
                ErrorCodes.NOT_FOUND)

        data = data.wrap()
        clean_nonserializable_attributes(data)
        return data

    def get_all(self):
        list = []
        data = kate5.query.filter(
            kate5.tenantId == self.auth_context.tenant_id)
        for data_item in data:
            data = data_item.wrap()
            clean_nonserializable_attributes(data)
            list.append(data)
        return list

    def save(self, model):
        new_data = kate5()
        for key in model:
            new_data.__setattr__(key, model[key])
        data = new_data
        data.tenantId = self.auth_context.tenant_id
        data.orgId = self.auth_context.org_id
        data.createdBy = self.auth_context.user_id
        data.createdDate = str(int(time.time()))
        data.modifiedBy = self.auth_context.user_id
        data.modifiedDate = str(int(time.time()))
        data.save()
        result = data.wrap()

        clean_nonserializable_attributes(result)
        return result

    def update(self, model, entity_id):

        record = kate5.query.get(entity_id)  # kate5 is a mongo class
        if record is None:
            raise kate5ServiceError(
                'kate5 {} not found'.format(entity_id),
                ErrorCodes.NOT_FOUND)

        for key in model:
            record.__setattr__(key, model[key])
        record.modifiedBy = self.auth_context.user_id
        record.modifiedDate = str(int(time.time()))
        record.save()
        result = record.wrap()
        clean_nonserializable_attributes(result)
        return result

    def delete(self, entity_id):
        if not self.auth_context.is_system_user:
            raise kate5ServiceError(
                'Delete operation is forbidden',
                ErrorCodes.NOT_ALLOWED)
        data = kate5.query.get(entity_id)
        if data is None:
            raise kate5ServiceError(
                'kate5 {} not found'.format(entity_id),
                ErrorCodes.NOT_FOUND)
        data.remove()
