# Idle Status Output Simulator

This tool lets you iterate on the CLI status output design **locally without AWS**. No need to launch engines or wait for sensor states - just edit the formatting functions and see the results instantly!

## Quick Start

```bash
# Show all scenarios
python -m dayhoff_tools.cli.engines_studios.idle_status_simulator

# Show specific scenario
python -m dayhoff_tools.cli.engines_studios.idle_status_simulator --scenario active_ssh_docker

# Show simple (non-detailed) output
python -m dayhoff_tools.cli.engines_studios.idle_status_simulator --scenario idle --simple
```

## Available Scenarios

- `idle` - Completely idle engine (all sensors inactive)
- `active_ssh_docker` - Active with SSH sessions and Docker workloads
- `active_ide` - Active with IDE connections only
- `coffee_lock` - Coffee lock active (keep-alive)
- `near_timeout` - Nearly timed out (28 min idle)
- `initializing` - Engine still booting up
- `stopped` - Stopped engine (no activity sensors shown)

## Workflow for Iterating on Design

### Option 1: Edit Current Formatter (Quick Tweaks)

1. Edit `dayhoff_tools/cli/engines_studios/progress.py`
2. Run simulator: `python -m dayhoff_tools.cli.engines_studios.idle_status_simulator --scenario <name>`
3. See changes instantly
4. Repeat until satisfied

### Option 2: Develop Enhanced Version (Major Redesign)

1. Edit `dayhoff_tools/cli/engines_studios/progress_colorful.py` (already has emoji-rich version)
2. Test standalone: `python -m dayhoff_tools.cli.engines_studios.progress_colorful`
3. Update simulator to use colorful version (see below)
4. When satisfied, replace functions in `progress.py`

#### Using Colorful Version in Simulator

Edit `idle_status_simulator.py` and change the import:

```python
# Replace this line:
from .progress import format_idle_state, format_time_ago

# With this:
from .progress_colorful import format_idle_state_colorful as format_idle_state
from .progress import format_time_ago
```

Then run: `python -m dayhoff_tools.cli.engines_studios.idle_status_simulator`

## Customization Ideas

The `progress_colorful.py` file has enhanced formatting with:

- **More emojis**: ☕ Coffee, 🐚 SSH, 💻 IDE, 🐳 Docker
- **Confidence badges**: 🔴 HIGH, 🟡 MEDIUM, ⚪ LOW
- **Progress bars**: Visual idle timer `[████████░░░░░░░░] 60%`
- **Icon-coded details**: 📦 containers, 🚫 ignored, 👤 sessions
- **Status emojis**: ⚡ Active, 💤 Idle

### Emoji Customization

Edit the emoji mappings in `progress_colorful.py`:

```python
sensor_emojis = {
    'coffee': '☕',   # Change to any emoji
    'ssh': '🐚',     # Try: 🔐, 🖥️, 🌐
    'ide': '💻',     # Try: 🖋️, 📝, ⌨️
    'docker': '🐳',  # Try: 📦, 🏗️, 🔧
}
```

### Add Custom Visualizations

Example - add a warning banner when nearly timed out:

```python
if idle_state.get('idle_seconds', 0) > 1500:  # > 25 minutes
    lines.insert(0, "⚠️  " + "="*56 + "  ⚠️")
    lines.insert(1, "⚠️  WARNING: Engine will shutdown in < 5 minutes!  ⚠️")
    lines.insert(2, "⚠️  " + "="*56 + "  ⚠️")
```

## Testing Your Changes

After editing formatters, test all scenarios to ensure nothing breaks:

```bash
# Quick test - show just one
python -m dayhoff_tools.cli.engines_studios.idle_status_simulator --scenario active_ssh_docker

# Full test - show all scenarios
python -m dayhoff_tools.cli.engines_studios.idle_status_simulator | less
```

## Integration with Real CLI

Once you're satisfied with your formatting:

1. Copy the functions from `progress_colorful.py` to `progress.py`
2. OR replace the imports in `engine_commands.py`:
   ```python
   from .progress_colorful import format_idle_state_colorful as format_idle_state
   ```

3. Test with real engine (optional):
   ```bash
   dh engine2 status <engine-name> --detailed --env sand
   ```

## Tips

- **Fast iteration**: Keep simulator running in a split terminal, edit code in another pane
- **Test empty states**: The `idle` scenario shows all sensors inactive - good for edge cases
- **Test full states**: The `active_ssh_docker` scenario shows everything active - good for layout
- **Test warnings**: The `near_timeout` scenario shows warning states
- **Unicode support**: Ensure your terminal supports emoji/unicode (most modern terminals do)

## Troubleshooting

**Emojis not displaying?**
- Check terminal font supports emoji
- Try simpler emojis (✓ ✗ work everywhere)

**Import errors?**
- Run from dayhoff-tools root: `cd /path/to/dayhoff-tools && python -m dayhoff_tools.cli.engines_studios.idle_status_simulator`

**Want to add new scenarios?**
- Edit `generate_scenarios()` in `idle_status_simulator.py`
- Follow the existing pattern for sensor states

