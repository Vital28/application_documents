import datetime
import sqlite3


class Contract:
    def __init__(self, id, name, creation_date, signing_date, status, project_id):
        self.id = id
        self.name = name
        self.creation_date = creation_date
        self.signing_date = signing_date
        self.status = status
        self.project_id = project_id

    def confirm_contract(self):
        if self.status == "Черновик":
            self.status = "Активен"
            self.signing_date = datetime.datetime.now()
            return True
        return False

    def complete_contract(self):
        if self.status == "Активен":
            self.status = "Завершен"
            return True
        return False


class Project:
    def __init__(self, id, name, creation_date):
        self.id = id
        self.name = name
        self.creation_date = creation_date


class ContractSystem:
    def __init__(self, db_name="contracts.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY,
                name TEXT,
                creation_date TEXT,
                signing_date TEXT,
                status TEXT,
                project_id INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                name TEXT,
                creation_date TEXT
            )
        ''')

        self.conn.commit()

    def create_contract(self, name):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM contracts WHERE name = ?', (name,))
        existing_contract = cursor.fetchone()

        if existing_contract:
            print("Договор с таким именем уже существует.")
            return None

        cursor.execute('''
            INSERT INTO contracts (name, creation_date, signing_date, status, project_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, datetime.datetime.now(), None, "Черновик", None))
        self.conn.commit()
        return Contract(cursor.lastrowid, name, datetime.datetime.now(), None, "Черновик", None)

    def create_project(self, name):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO projects (name, creation_date)
            VALUES (?, ?)
        ''', (name, datetime.datetime.now()))
        self.conn.commit()
        return Project(cursor.lastrowid, name, datetime.datetime.now())

    def add_contract_to_project(self, project_name, contract_name):
        cursor = self.conn.cursor()

        # Проверка существования проекта
        cursor.execute('SELECT id FROM projects WHERE name = ?', (project_name,))
        project_id = cursor.fetchone()
        if not project_id:
            print(f"Проект '{project_name}' не найден.")
            return False

        # Проверка существования и активности договора
        cursor.execute('SELECT id FROM contracts WHERE name = ? AND status = ?', (contract_name, 'Активен'))
        contract_id = cursor.fetchone()
        if not contract_id:
            print(f"Договор '{contract_name}' не найден или не активен.")
            return False

        # Проверка наличия активного договора в проекте
        cursor.execute('SELECT id FROM contracts WHERE project_id = ? AND status = ?', (project_id[0], 'Активен'))
        active_contract = cursor.fetchone()
        if active_contract:
            print(f"В проекте уже есть активный договор.")
            return False

        # Обновление поля project_id у договора
        cursor.execute('UPDATE contracts SET project_id = ? WHERE id = ?', (project_id[0], contract_id[0]))
        self.conn.commit()
        print(f"Договор '{contract_name}' добавлен в проект '{project_name}'.")
        return True

    def list_contracts(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM contracts')
        contracts = cursor.fetchall()

        for contract in contracts:
            project_name = "Нет проекта"
            if contract[5]:
                cursor.execute('SELECT name FROM projects WHERE id = ?', (contract[5],))
                project_name = cursor.fetchone()[0]

            print(f"Договор '{contract[1]}': Статус - {contract[4]}, Проект - {project_name}")

    def list_projects(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM projects')
        projects = cursor.fetchall()

        for project in projects:
            print(f"Проект '{project[1]}': Дата создания - {project[2]}")

    def confirm_contract(self, contract_name):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM contracts WHERE name = ? AND status = ?', (contract_name, 'Черновик'))
        contract = cursor.fetchone()

        if contract:
            cursor.execute('''
                UPDATE contracts
                SET signing_date = ?, status = ?
                WHERE id = ?
            ''', (datetime.datetime.now(), "Активен", contract[0]))
            self.conn.commit()
            return True
        return False

    def complete_contract(self, contract_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM contracts WHERE id = ?', (contract_id,))
        self.conn.commit()
        return True


def main():
    system = ContractSystem()

    while True:
        print("Выберите действие:")
        print("1. Создать договор")
        print("2. Создать проект")
        print("3. Просмотреть список договоров")
        print("4. Просмотреть список проектов")
        print("5. Подтвердить договор")
        print("6. Завершить договор")
        print("7. Добавить договор к проекту")
        print("8. Завершить работу")

        choice = input("Введите номер действия: ")

        if choice == "1":
            name = input("Введите название договора: ")
            system.create_contract(name)

        elif choice == "2":
            name = input("Введите название проекта: ")
            system.create_project(name)

        elif choice == "3":
            system.list_contracts()

        elif choice == "4":
            system.list_projects()

        elif choice == "5":

            contract_name = input("Введите название договора для подтверждения: ")

            if system.confirm_contract(contract_name):

                print(f"Договор '{contract_name}' подтвержден.")

            else:

                print("Договор не найден или не может быть подтвержден.")

        elif choice == "6":

            contract_name = input("Введите название договора для завершения: ")

            if system.complete_contract(contract_name):

                print(f"Договор '{contract_name}' завершен.")

            else:

                print("Договор не найден или не может быть завершен.")

        elif choice == "7":

            contract_name = input("Введите название договора для добавления в проект: ")
            project_name = input("Введите название проекта, к которому добавить договор: ")
            system.add_contract_to_project(project_name, contract_name)

        elif choice == "8":
            break


if __name__ == "__main__":
    main()
