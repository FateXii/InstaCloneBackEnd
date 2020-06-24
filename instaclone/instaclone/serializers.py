from rest_framework import serializers


# class DetailSerializer(serializers.RelatedField):
#     def to_representation(self, instance):
#         output = {}
#         for attr_name in instance.__dict__.keys():
#             attr = instance.__dict__[str(attr_name)]
#             if attr_name.startswith('_'):
#                 pass
#             elif hasattr(attr, '__call__'):
#                 pass
#             elif isinstance(attr, (int, bool, float, type(None))):
#                 output[attr_name] = attr
#             elif isinstance(attr, list):
#                 output[attr_name] = [
#                     self.to_representation(item) for item in attr]
#             elif isinstance(attr, dict):
#                 output[attr_name] = {
#                     str(key): self.to_representation(value) for key, value in
#                     attr.items()
#                 }
#             elif attr_name == 'replies':
#                 output[attr_name] = [
#                     self.to_representation(item) for item in attr]
#             else:
#                 output[attr_name] = str(attr)
#         return output
