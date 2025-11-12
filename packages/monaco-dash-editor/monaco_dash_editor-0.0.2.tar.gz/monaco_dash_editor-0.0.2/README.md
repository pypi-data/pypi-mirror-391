# monaco_dash_editor

monaco_dash_editor is a Dash component library.

Monaco Editor for Dash

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md)

### Installation
```
$ pip install monaco-dash-editor
```

### Example Usage
https://github.com/user-attachments/assets/59775e71-5948-4607-8131-f07549aa3cea

```
MonacoDashEditor(
    id="json-editor",
    language="json",
    height="300px",
    value="""{
        "name": "John Doe",
        "age": 30,
        "city": "New York",
        "isStudent": false,
        "hobbies": [
            "reading",
            "swimming",
            "coding"
        ]
    }""",
    options={
        "minimap": {"enabled": False},
        "formatOnType": True
    }
)
```

