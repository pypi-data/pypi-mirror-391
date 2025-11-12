# SCL (Python) — usage guide

This is a usage-focused guide. For the full SCL specification, see the root README.  
Full documentation: [click](https://gitlab.com/shareui/scl/-/blob/main/README.md?ref_type=heads)

## Installation

```bash
pip install structcfg-parser
```

Or in `requirements.txt`:
```
structcfg-parser==1.1.0
```

## Import and quick start

```python
import scl_parser

# From file
config = scl_parser.load("config.scl")

# From string
config = scl_parser.loads("count :: num { 42 }")

# To file
scl_parser.dump(config, "output.scl")

# To string
s = scl_parser.dumps(config)
```

## Examples

```python
import scl_parser

cfg = scl_parser.loads("""
app :: class {
  name :: str { "Demo" }
  debug :: bool { true }
  ports :: list(num) { 80, 443 }
  price :: fl { 19.99 }
  note :: ml {
    'hello
    world'
  }
}
""")
print(cfg["app"]["name"])
```

## License

MIT License