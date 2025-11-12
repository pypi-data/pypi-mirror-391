# StopWeb

Block websites permanently to help you stay focused. Works by editing your system's hosts file. You can also set a temporary duration if needed.

I built this because I kept getting distracted by social media and news sites when trying to work. Simple solution: block them until you decide to unblock.

## What it does

- Blocks websites until you manually unblock them
- Works on Mac, Linux, and Windows
- Lets you see what's currently blocked
- Can unblock sites early if needed

## Install

 
```bash
pip install stopweb
```

## Basic usage

Block Facebook permanently:

```bash
sudo stopweb facebook.com
```

Block multiple sites at once:

```bash
sudo stopweb facebook.com youtube.com reddit.com
```

See what's blocked:

```bash
sudo stopweb --list
```

Unblock a site:

```bash
sudo stopweb --remove facebook.com
```

Remove all blocks:

```bash
sudo stopweb --clear
```

Temporarily block a site (expires automatically):

```bash
sudo stopweb -d 2h twitter.com      # 2 hours
sudo stopweb --duration 1d reddit.com  # 1 day
```

## How it works

StopWeb edits your hosts file to redirect blocked sites to localhost (127.0.0.1).

On Mac/Linux that's `/etc/hosts`, on Windows it's `C:\Windows\System32\drivers\etc\hosts`.

It adds lines like:

```text
127.0.0.1    facebook.com    # StopWeb:
# For temporary blocks, an expiry is recorded, e.g.
127.0.0.1    twitter.com     # StopWeb: expires=2025-01-01T12:00:00
```

Blocked sites stay blocked until you run the remove or clear command.

## Notes

- Requires sudo/admin privileges (needs to edit system files)
- You might need to clear your browser cache after blocking/unblocking
- Creates a backup of your hosts file before making changes
- If something goes wrong, your original hosts file is saved as `hosts.stopweb_backup`
- Temporary blocks are removed automatically by running `stopweb --cleanup`

## Notifications (manual edits)

StopWeb can alert you if someone edits your hosts file and removes or changes StopWeb entries by hand. It does not notify on additions.

- Default recipient: `linj1@tcd.ie`
- Snapshot is checked whenever you run a StopWeb command; if differences are found since the last run, an email is sent (or a file is saved in `~/.config/stopweb/outbox/` if SMTP isn't configured).
- To configure SMTP, edit `~/.config/stopweb/stopweb.json` and set `settings.notifications.smtp` fields.

What triggers a notification:

- StopWeb line removed from hosts (e.g., someone deleted `# StopWeb:` lines)
- StopWeb line modified (e.g., IP or expires metadata changed)

What does not trigger a notification:

- Adding new StopWeb entries
- Normal StopWeb commands you run yourself (block/remove/clear/cleanup)

## Audit and Watch

Single-run audit:

```bash
sudo stopweb --audit
```

Continuous watch (poll every 15 seconds):

```bash
sudo stopweb --watch --interval 15
```

Tip: for testing without touching your real hosts file, set an override:

```bash
export STOPWEB_HOSTS_PATH="/tmp/stopweb-hosts"
```

Then put some lines into that file and run `stopweb --audit` or `--watch`.

## Why not just use browser extensions?

Browser extensions can be easily disabled when you're feeling weak. Editing the hosts file is more permanent - you'd have to remember the exact command to undo it.

Plus this works system-wide, not just in your browser.
