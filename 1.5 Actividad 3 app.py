import os
import oracledb
from dotenv import load_dotenv

load_dotenv()

#Configuracion de conexion (se lee del archivo .env)
#Se necesita configurar el .env manualmente, viene incluido como env.example

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")

def conectar():#devuelve una conexion a la base de datos de freesql
    try:
        conexion = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN,
        )
        return conexion
    except oracledb.DatabaseError as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

#CREATE

def crear_job():
    job_id = input("Ingrese job_id (max 10 caracteres): ").strip()
    job_title = input("Ingrese job_title: ").strip()
    min_salary = input("Ingrese min_salary (o Enter para omitir): ").strip()
    max_salary = input("Ingrese max_salary (o Enter para omitir): ").strip()

    min_salary = int(min_salary) if min_salary else None
    max_salary = int(max_salary) if max_salary else None

    conexion = conectar()
    if not conexion:
        return
    try:#Insertar en jobs
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO jobs (job_id, job_title, min_salary, max_salary)
            VALUES (:job_id, :job_title, :min_salary, :max_salary)
            """,
            job_id=job_id,
            job_title=job_title,
            min_salary=min_salary,
            max_salary=max_salary,
        )
        conexion.commit()
        print("Registro insertado correctamente.")
    except oracledb.DatabaseError as e:
        print(f"Error al insertar: {e}")
    finally:
        cursor.close()
        conexion.close()

#READ

def leer_jobs():
    conexion = conectar()
    if not conexion:
        return
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT job_id, job_title, min_salary, max_salary FROM jobs ORDER BY job_id")
        filas = cursor.fetchall()

        if not filas:
            print("No hay registros en la tabla jobs.")
            return

        print(f"\n{'JOB_ID':<10}{'JOB_TITLE':<35}{'MIN_SALARY':<12}{'MAX_SALARY':<12}")
        print("-" * 69)
        for job_id, job_title, min_salary, max_salary in filas:
            print(f"{job_id:<10}{job_title:<35}{str(min_salary or ''):<12}{str(max_salary or ''):<12}")
        print()
    except oracledb.DatabaseError as e:
        print(f"Error al leer: {e}")
    finally:
        cursor.close()
        conexion.close()


def buscar_job(job_id):
    conexion = conectar()
    if not conexion:
        return None
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT job_id, job_title, min_salary, max_salary FROM jobs WHERE job_id = :id", id=job_id)
        return cursor.fetchone()
    except oracledb.DatabaseError as e:
        print(f"Error al buscar: {e}")
        return None
    finally:
        cursor.close()
        conexion.close()

#UPDATE

def actualizar_job():
    job_id = input("Ingrese job_id a actualizar: ").strip()

    registro = buscar_job(job_id)
    if not registro:
        print("No existe un job con ese job_id.")
        return

    print(f"Registro actual: {registro}")
    job_title = input("Nuevo job_title (Enter para no cambiar): ").strip()
    min_salary = input("Nuevo min_salary (Enter para no cambiar): ").strip()
    max_salary = input("Nuevo max_salary (Enter para no cambiar): ").strip()

    campos = []
    valores = {"id": job_id}

    if job_title:
        campos.append("job_title = :job_title")
        valores["job_title"] = job_title
    if min_salary:
        campos.append("min_salary = :min_salary")
        valores["min_salary"] = int(min_salary)
    if max_salary:
        campos.append("max_salary = :max_salary")
        valores["max_salary"] = int(max_salary)

    if not campos:
        print("No se ingreso ningun cambio.")
        return

    consulta = f"UPDATE jobs SET {', '.join(campos)} WHERE job_id = :id"

    conexion = conectar()
    if not conexion:
        return
    try:
        cursor = conexion.cursor()
        cursor.execute(consulta, valores)
        conexion.commit()
        print("Registro actualizado correctamente.")
    except oracledb.DatabaseError as e:
        print(f"Error al actualizar: {e}")
    finally:
        cursor.close()
        conexion.close()

#DELETE

def eliminar_job():
    job_id = input("Ingrese job_id a eliminar: ").strip()

    registro = buscar_job(job_id)
    if not registro:
        print("No existe un job con ese job_id.")
        return

    confirmar = input(f"Seguro que desea eliminar '{job_id}'? (s/n): ").strip().lower()
    if confirmar != "s":
        print("Operacion cancelada.")
        return

    conexion = conectar()
    if not conexion:
        return
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM jobs WHERE job_id = :id", id=job_id)
        conexion.commit()
        print("Registro eliminado correctamente.")
    except oracledb.DatabaseError as e:
        print(f"Error al eliminar: {e}")
    finally:
        cursor.close()
        conexion.close()

#MENU PRINCIPAL

def menu():
    while True:
        print("1. Create")
        print("2. Read")
        print("3. Update")
        print("4. Delete")
        print("5. Salir")
        opcion = input("Seleccione una opcion: ").strip()

        if opcion == "1":
            crear_job()
        elif opcion == "2":
            leer_jobs()
        elif opcion == "3":
            actualizar_job()
        elif opcion == "4":
            eliminar_job()
        elif opcion == "5":
            print("Saliendo...")
            break
        else:
            print("Opcion invalida, intente de nuevo.")


if __name__ == "__main__":
    menu()

