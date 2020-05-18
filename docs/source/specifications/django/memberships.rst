.. membership-page:

Memberships
===========

.. _studio_memberships:

Studio memberships
------------------

.. csv-table:: членство в студии
   :header: "description", "модель", "прим"
   :widths: 50, 25, 50

   "Запросы на вступление в студию", " **RequestFromUser** ", "создаёт артист, принимает или отказывает студия"
   "Приглашения от студии", " **InvitationToUser** ", "создаёт студия, принимает или отказывает артист"
   "Принятие, увольнение участников студии", " **StudioMember** ", "привязать к закону о труде, через заявления и прочее."

.. _group_memberships:

Group memberships
-----------------

.. csv-table:: членство в группах студии
   :header: "description", "модель", "прим"
   :widths: 50, 25, 50

   "Добавление и удаление пользователей", " **auth.models.Group** ", ""

.. _workroom_memberships:

Workroom memberships
--------------------

.. csv-table:: членство в отделах студии
   :header: "description", "модель", "прим"
   :widths: 50, 25, 50

   "Добавление и удаление пользователей", " **WorkroomMember** ", ""