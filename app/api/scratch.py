# def test_staff_user_fields_read_only(self):
#     """Tests if the taskserializer is setting all fields to read only
#     false for staff users except the id field"""

#     factory = RequestFactory()
#     self.user2.is_staff = True
#     url = reverse('task-list')
#     data = {
#         'title': 'The first Task',
#         'description': 'The task to be tested.',
#         'due_date': date(2023, 1, 15),
#         'category': self.category.name,
#         'priority': self.priority.caption,
#         'status': self.status.caption,
#     }
#     request = factory.post(url, data=data, user=self.user2)

#     view = views.TaskView(request)
#     serializer = StaffTaskSerializer(
#         instance=self.task,
#         context={'request': request, 'view': view}
#     )

#     fields = serializer.fields
#     # ID field is read only by default
#     fields.pop('id', None)

#     # Checks if all other fields are modifiable
#     for field in fields:
#         self.assertFalse(fields[field].read_only)
