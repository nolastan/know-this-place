# The MCP server

`mcp/server.py` exposes the site to AI chat clients as an
[MCP](https://modelcontextprotocol.io) server. It is one stdlib-only Python
file, and it is not part of the build. It reads only files the repository
already holds: each page's `data.json` or `place.json`, `corpus.jsonl`, and
`shared/addresses.geojson`. If `addresses.geojson` is missing, the server runs
`scripts/build_map_index.py` once to make it. The server never writes anything.

## Tools

| Tool | Does |
|---|---|
| `find_building` | address ("429 Castro St") or name ("Castro Theatre") to matching pages |
| `get_building` | one page as structured data: identity, building facts, landmark and district, notable past residents, businesses, the dated history, recent permits, sources |
| `nearby` | pages near a point or another page, nearest first |
| `browse` | neighborhoods, then a neighborhood's streets and parks, then a street's addresses |
| `search` | the whole corpus, by neighborhood, year built, how far back the history goes, use, district, words in the summary |

## Rules

- **Read-only, and nothing a page doesn't show.** `get_building` follows the
  page. It uses `description_edited` over a permit's raw text, shows only
  businesses for `occupants`, and gives every fact with its source.
- **No lookup by a person's name.** Names are matched only against page
  headings, which are building and place names. Don't add a tool or a search
  field over `notable_residents`, permits or any other text that names people
  (AGENTS.md → Privacy).
- **Surveys are sources, not content.** Leave out a survey's name and values
  that say nothing, such as `Unevaluated` (`UNINFORMATIVE_STATUS`).
- **Stdlib only.** The no-dependencies rule applies here too, so there's no
  MCP SDK. The protocol is plain JSON-RPC, over stdio or one HTTP endpoint.
- **Keep it in step with `data.json`.** If a field it reads is renamed, change
  `building_summary`, and check `/llms.txt` as well.

## Trying it

Run it from a clone of this repository. It needs Python 3.9 or later, so the `python3` that ships with macOS works.

Each client needs the server's **full path**. Print it from the root of your
clone with `echo "$(pwd)/mcp/server.py"`. A path starting `/mcp/` is wrong.

**Claude Code:** run this from the root of the clone, then start `claude` in
the same folder. `/mcp` there should list `know-this-place` as connected. The
server exists only in the terminal Claude Code, not in the Claude app.

```bash
claude mcp add know-this-place -- python3 "$(pwd)/mcp/server.py"
```

**Claude Desktop** (the app, which is what most chats run in): Settings →
Developer → Edit Config, then add this to `claude_desktop_config.json`, put
your clone's full path in `args`, and quit and reopen the app. The tools
appear under the chat box's tools menu. If the server doesn't start, use
`/usr/bin/python3` as the command, because the app doesn't read your shell's
`PATH`.

```json
{
  "mcpServers": {
    "know-this-place": {
      "command": "python3",
      "args": ["/Users/you/Repos/know-this-place/mcp/server.py"]
    }
  }
}
```

**Over HTTP**, the way a hosted copy would run:

```bash
python3 mcp/server.py --http 8765
claude mcp add --transport http know-this-place http://127.0.0.1:8765/mcp
```

Then ask something like "What's the history of 730 Montgomery Street?" or
"What are the oldest buildings in North Beach?"

Claude on the web and in the mobile apps can only reach a server hosted on the
public internet. Hosting it means running `--http` with `--host 0.0.0.0` on a
small host, behind HTTPS, from a checkout of `main`.
