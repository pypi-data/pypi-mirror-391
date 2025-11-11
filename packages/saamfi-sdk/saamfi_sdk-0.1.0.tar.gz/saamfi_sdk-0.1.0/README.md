## Saamfi SDK para Python

Cliente oficial en Python para integrar sistemas con los servicios de autenticacion y autorizacion de Saamfi. Este SDK expone las mismas operaciones disponibles en la libreria Java (`SaamfiDelegate`) y simplifica la validacion de tokens JWT, la autenticacion de usuarios y la consulta de informacion institucional.

---

## Instalacion

- **Desde PyPI**
  ```bash
  pip install saamfi-sdk
  ```
- **Desde el codigo fuente**
  ```bash
  git clone https://github.com/saamfi/saamfi-sdk-python.git
  cd saamfi-sdk-python
  pip install -e .
  ```

Configura las siguientes variables de entorno antes de usar el cliente (por ejemplo en un archivo `.env`):

- `SAAMFI_BASE_URL`: URL base del servicio Saamfi (`https://api.saamfi.com`).
- `SAAMFI_SYS_ID`: Identificador del sistema o tenant asignado por Saamfi.
- `SAAMFI_TENANT_ID` *(opcional)*: Identificador de institución (para endpoints como `/institutions/{instid}/params`).
- `SAAMFI_CLIENT_ID` y `SAAMFI_CLIENT_SECRET` *(opcionales)*: Credenciales del sistema si tu integración las requiere.
- `SAAMFI_TEST_USERNAME` y `SAAMFI_TEST_PASSWORD` *(solo para pruebas locales)*: Usuario demo del sandbox.

> El cliente mantiene compatibilidad con las variables antiguas `SAAMFI_URL`, `SAAMFI_SYSTEM_ID` y `SAAMFI_INST_ID`.

---

## Quickstart

```python
from saamfi_sdk import SaamfiClient

client = SaamfiClient()  # Usa SAAMFI_BASE_URL y SAAMFI_SYS_ID desde el entorno

response = client.login("usuario@example.com", "clave-segura")
if response:
    print(f"Token: {response.access_token}")
    token_info = client.validate_token(response.access_token)
    print(f"Roles: {token_info.roles}")
else:
    print("Credenciales invalidas")
```

---

## Sandbox local con docker compose

1. Levanta el entorno local de Saamfi con `docker compose` (puerto `9091` según la configuración compartida).
2. Crea un archivo `.env` junto al proyecto del SDK con las variables:
   ```
   SAAMFI_BASE_URL=http://localhost:9091/iaslab/saamfiapi
   SAAMFI_SYS_ID=8
   SAAMFI_CLIENT_ID=8
   SAAMFI_CLIENT_SECRET=qYr6-CxZP9t4vN2eFM1sR4gL
   SAAMFI_TENANT_ID=1
   SAAMFI_TEST_USERNAME=testuser
   SAAMFI_TEST_PASSWORD=password123
   ```
3. Ejecuta el script de ejemplo:
   ```bash
   python examples/sandbox_demo.py
   ```
   Verás el flujo completo: descarga de clave pública, descubrimiento de sistemas/instituciones, autenticación del usuario demo, validación del JWT y consultas protegidas.

> Consulta los logs del backend en `saamfi-rest/logs/saamfi.log` o mediante `GET /logs/` (requiere rol `Query-server-logs`) para corroborar las operaciones.

---

## Ejemplos por funcionalidad

Cada metodo del cliente refleja una operacion del servicio Saamfi. Los siguientes fragmentos muestran el flujo completo con un token valido (`token`):

- **Obtener llave publica**
  ```python
  public_key = client.get_public_key()
  ```

- **Autenticar usuario**
  ```python
  login = client.login("usuario@example.com", "clave")
  ```

- **Validar token y extraer datos**
  ```python
  token_info = client.validate_token(token)
  print(token_info.username, token_info.roles)
  ```

- **Roles desde un JWT**
  ```python
  roles = client.get_roles_from_jwt(token)
  ```

- **Informacion detallada de usuario**
  ```python
  user = client.get_user_info(token, user_id=12345)
  ```

- **Buscar usuario por username**
  ```python
  user = client.get_user_by_username(token, "john.doe")
  ```

- **Buscar usuarios por documentos**
  ```python
  users = client.get_users_by_document(token, ["100200300", "999888777"])
  ```

- **Obtener usuarios por lista de IDs**
  ```python
  users_json = client.get_users_from_list(token, [1, 2, 3])
  ```

- **Busqueda generica por parametro y valor**
  ```python
  result_json = client.get_users_by_param_and_value(token, "email", "example.com")
  ```

- **Consultar institucion por NIT**
  ```python
  institution_json = client.get_institution_by_nit(token, "900123456-7")
  ```

- **Consultar instituciones por IDs**
  ```python
  institutions_json = client.get_institutions_by_ids(token, [10, 20, 30])
  ```

- **Listado público de sistemas e instituciones**
  ```python
  systems = client.list_public_systems()
  institutions = client.list_public_institutions()
  ```

- **Parámetros de institución**
  ```python
  params = client.get_institution_params(token)  # Usa SAAMFI_TENANT_ID por defecto
  ```

- **Roles configurados para un sistema**
  ```python
  roles = client.get_system_roles(token)  # Usa SAAMFI_SYS_ID por defecto
  ```

---

## Referencia de API

### Clases principales

| Clase | Descripcion |
| ----- | ----------- |
| `SaamfiClient` | Cliente principal; gestiona autenticacion, validacion y consultas. |
| `LoginBody` | Modelo para solicitudes de login. |
| `LoginResponse` | Respuesta de autenticacion exitosa. |
| `UserInfo` | Informacion detallada de usuario. |
| `UserDetailToken` | Datos extraidos de un JWT validado. |

### Metodos clave de `SaamfiClient`

| Metodo | Entrada | Salida | Nota |
| ------ | ------- | ------ | ---- |
| `get_public_key()` | - | `RSAPublicKey` | Obtiene y cachea la llave publica. |
| `login(username, password)` | `str`, `str` | `LoginResponse | None` | Autentica usuario. |
| `get_roles_from_jwt(auth_token)` | `str` | `List[str]` | Extrae claim `role`. |
| `validate_token(auth_token)` | `str` | `UserDetailToken` | Valida firma y claims. |
| `get_user_info(auth_token, user_id)` | `str`, `int` | `UserInfo | None` | Consulta usuario por ID. |
| `get_user_by_username(auth_token, username)` | `str`, `str` | `dict | None` | Consulta POST por username. |
| `get_users_by_document(auth_token, user_documents)` | `str`, `List[str]` | `List[dict]` | Busca por multiples documentos. |
| `get_users_from_list(auth_token, user_ids)` | `str`, `List[int]` | `str | None` | JSON con usuarios por ID. |
| `get_users_by_param_and_value(auth_token, param, value)` | `str`, `str`, `str` | `str | None` | Filtro generico usando query string. |
| `get_institution_by_nit(auth_token, nit)` | `str`, `str` | `str | None` | Consulta institucion por NIT. |
| `get_institutions_by_ids(auth_token, institution_ids)` | `str`, `List[int]` | `str | None` | Consulta masiva por IDs. |
| `list_public_institutions()` | - | `List[dict] | None` | Descubrimiento de instituciones disponibles. |
| `get_institution_params(auth_token, institution_id=None)` | `str`, `Optional[int]` | `dict | None` | Obtiene parámetros de configuración institucional. |
| `list_public_systems()` | - | `List[dict] | None` | Descubrimiento de sistemas publicados. |
| `get_system_roles(auth_token, system_id=None)` | `str`, `Optional[int]` | `List[dict] | None` | Roles disponibles para un sistema. |

> Consulta los docstrings en `saamfi_sdk/client.py` para conocer detalles, equivalencias con la version Java y ejemplos adicionales.

---

## Manejo de errores

Todas las excepciones del SDK heredan de `SaamfiException`:

| Excepcion | Cuándo ocurre |
| --------- | ------------- |
| `SaamfiAuthenticationError` | Credenciales invalidas o token sin permisos. |
| `SaamfiTokenValidationError` | Token expirado, mal formado o con claims faltantes. |
| `SaamfiConnectionError` | Problemas de red o respuestas no exitosas del backend. |
| `SaamfiInvalidSystemError` | El token pertenece a otro `system_id`. |
| `SaamfiUnauthorizedError` | El usuario autenticado no tiene permisos para la operacion. |
| `SaamfiNotFoundError` | El recurso solicitado no existe. |

```python
from saamfi_sdk import SaamfiClient
from saamfi_sdk.exceptions import SaamfiConnectionError, SaamfiAuthenticationError

client = SaamfiClient()

try:
    login = client.login("usuario@example.com", "clave")
except SaamfiConnectionError as exc:
    print(f"No es posible comunicar con Saamfi: {exc}")
except SaamfiAuthenticationError:
    print("Credenciales invalidas")
```

---

