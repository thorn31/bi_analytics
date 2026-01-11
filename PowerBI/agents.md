# Agent Notes

## Requesting write operations

- Before calling any write operation (updates to measures, tables, etc.), first ask the user for explicit confirmation describing exactly what will be changed.
- Only after the user confirms, issue the write command immediately so the prompt they receive matches the approved action.
- If the user declines or does not respond, do not attempt the write and wait for further direction.
