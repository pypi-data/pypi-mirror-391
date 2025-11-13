# a11y-checker

`a11y-checker` is an **asynchronous Python client** for the [Accessibility Checker API](https://wcag.dock.codes/documentation/api-accessibility-checker/) - a tool for **automated accessibility audits** based on WCAG 2.1 / 2.2.  
It lets you easily scan, re-scan, and analyze websites directly from your Python applications.

---

### Features

- Fully asynchronous (non-blocking)
- Multi-language and device scanning
- Fetch, re-scan, or delete audits

---

### Installation

```shell
pip install a11y-checker
```
## Usage Example
```python
import asyncio
from a11y_checker import A11yCheckerClient, Device, Language

async def main():
    async with A11yCheckerClient() as guest:
        # Run a new audit
        audit_request = await guest.scan("https://example.com", lang=Language.EN, device=Device.DESKTOP)
        print(audit_request)

        # Get audit
        audit = await guest.audit(uuid=audit_request['uuid'])
        print(audit)

        # Delete an audit
        await guest.delete_audit(audit['uuid'])

asyncio.run(main())
```
### 🔑 Get Your API Key

You can test as a guest, request an API key, or test the service directly on the website:

👉 https://wcag.dock.codes/contact-us/

### Enums
| Enum            | Description               | Example                                                            |
| --------------- | ------------------------- | ------------------------------------------------------------------ |
| **Language**    | Language for audits       | `Language.EN`, `Language.PL`, `Language.DE`                        |
| **Device**      | Device type for scanning  | `Device.DESKTOP`, `Device.MOBILE`, `Device.ALL`                    |
| **AuditStatus** | Filter audits by status   | `AuditStatus.PASSED`, `AuditStatus.FAILED`, `AuditStatus.TO_TESTS` |
| **Sort**        | Sorting order for results | `Sort.CREATED_AT_DESC`, `Sort.LAST_AUDIT_ASC`                      |

### Available Methods
| Method                                                                                                                        | Description                                                        |
|-------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| `scan(url: str, lang: Language, device: Device, sync: bool, extra_data: bool, unique_key: Optional[str], key: Optional[str])` | Run a new accessibility scan for a given URL.                      |
| `audit(uuid: str, lang: Language, extra_data: bool key: Optional[str])`                                                       | Get detailed results of a specific audit.                          |
| `audits(search: str, page: int, per_page: int, sort: Sort, unique_key: Optional[str], key: Optional[str])`                    | Fetch paginated audits with optional filtering and sorting.        |
| `rescan(uuid: str, lang: Language, sync: bool, extra_data: bool = False)`                                                     | Trigger a re-scan of an existing audit.                            |
| `history(uuid: str, page: int, per_page: int, sort: Sort, key: Optional[str])`                                                | Fetch paginated audit history with optional filtering and sorting. |
| `delete_audit(uuid: str, key: Optional[str])`                                                                                 | Delete an existing audit.                                          |
| `delete_history(uuid: str, key: Optional[str])`                                                                               | Delete audit history.                                              |
| `user(key: Optional[str])`                                                                                                    | Get current user data.                                             |
| `update_audit_manual(uuid: str, criterion_id: int, status: AuditStatus, device: Device, key: Optional[str])`                  | Updating the status of a single criterion from a manual audit.     |

### Advanced Example: Parallel Audits
```python
import asyncio
from a11y_checker import A11yCheckerClient

async def main():
    async with A11yCheckerClient(api_key="your-api-key") as client:
        results = await asyncio.gather(
            client.audit(uuid="uuid1"),
            client.audit(uuid="uuid2"),
            client.audit(uuid="uuid3"),
        )
        print(results)

asyncio.run(main())
```
🤝 Contributing
Contributions are welcome!
If you find a bug or want to improve the library, please open an issue or pull request on
👉 [GitHub](https://github.com/dockcodes/a11y-checker-python/issues)