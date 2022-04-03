# CEKit module description for the [ConTeXt](https://wiki.contextgarden.net) typesetting tools

## TEXMFHOME

I think the current (default-as-installed) TEXMFHOME for ConTeXt is set to
`/root/texmf`.

This can be overridden by explicitly setting the TEXMFHOME environment
variable and then running:

```
  mtxrun --generate
```

**Alternatively** you can update one of the following `texmf.cnf` files:

1. /opt/context/bin/x86_64-linux/texmf.cnf
2. /opt/context/bin/texmf.cnf
3. /opt/context/texmf.cnf
4. /opt/context/texmf/web2c/texmf.cnf

(which are read in the above order), to read as (for example):

```
 return {
   content = {
     variables = {
       TEXMFHOME = "/root/context/texmf-local",
     },
   },
 }

```

and then running:

```
  mtxrun --generate
```

(See: [ConTeXtGarden: Custom
Configuration](https://wiki.contextgarden.net/Custom_Configuration))
