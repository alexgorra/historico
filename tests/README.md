# Testing Documentation

## Pytest Infrastructure for Movement Mechanics

This project now includes a complete pytest testing infrastructure for validating player movement mechanics in the multiplayer Pygame project.

### Setup Complete ✓

- **Test Directory**: `tests/`
- **Configuration**: `pytest.ini`
- **Mock Framework**: Pygame headless mocking in `tests/conftest.py`
- **Test Suite**: `tests/test_movement.py`

### What's Tested

#### 1. Basic Movement (4 tests)
- ✅ Arrow key movement (RIGHT moves player right by PLAYER_SPEED)
- ✅ WASD movement (A moves player left by PLAYER_SPEED)
- ✅ Diagonal movement (UP + RIGHT moves both directions)
- ✅ No movement when no keys pressed

#### 2. Boundary Enforcement (4 tests)
- ✅ Cannot move past left boundary (x=0)
- ✅ Cannot move past right boundary (x=WIDTH-PLAYER_SIZE)
- ✅ Cannot move past top boundary (y=0)
- ✅ Cannot move past bottom boundary (y=HEIGHT-PLAYER_SIZE)

#### 3. Collision Detection (3 tests)
- ✅ Movement blocked when colliding with another player
- ✅ Movement allowed when players are far apart
- ✅ Collision detected with partially overlapping players

**Total: 11 tests — all passing ✓**

---

## Running Tests

### In Terminal

```bash
# Activate virtual environment (if not already active)
source .venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test class
pytest tests/test_movement.py::TestBasicMovement -v

# Run single test
pytest tests/test_movement.py::TestBasicMovement::test_move_right_with_arrow_key -v

# Run with coverage (if needed)
pytest tests/ --cov=src --cov-report=html
```

### In VS Code

#### Method 1: Using Testing Tab
1. Click the **Testing** icon in the left sidebar (flask/beaker icon)
2. VS Code will auto-discover tests
3. Click ▶️ to run individual tests or test classes
4. View results inline with ✓/✗ indicators

#### Method 2: Using Command Palette
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Python: Configure Tests"
3. Select "pytest"
4. Select "tests" directory
5. Tests will appear in the Testing tab

#### Method 3: Terminal in VS Code
1. Open integrated terminal (`Ctrl+`` `)
2. Run pytest commands as shown above

---

## Test Structure

### Configuration Files

#### `pytest.ini`
- Test discovery patterns
- Output formatting
- Test markers (movement, collision, boundary)
- Python version requirements

#### `tests/conftest.py`
Key fixtures:
- **`mock_pygame`** (autouse, session-scoped): Mocks Pygame for headless testing
  - Mocks display, clock, events, key presses
  - Provides `MockRect` for collision testing
  - Prevents "No display" errors
  
- **`input_handler`**: Provides fresh `InputHandler` instance with reset key state

- **`sample_player_position`**: Returns `{'x': 400, 'y': 300}`

- **`sample_other_players`**: Returns dict of other players for collision tests

### Writing New Tests

```python
def test_new_movement_feature(self, input_handler, mock_pygame):
    """Test description here."""
    from game_constants import PLAYER_SPEED
    
    # Set up key state
    mock_pygame._key_array.set_keys({
        mock_pygame.K_RIGHT: True,
        # ... other keys set to False
    })
    
    # Initial state
    current_x, current_y = 100, 100
    other_players = {}
    
    # Execute
    new_x, new_y, moved = input_handler.handle_input(current_x, current_y, other_players)
    
    # Assert
    assert new_x == current_x + PLAYER_SPEED
    assert moved is True
```

---

## Key Features

### Headless Testing
- No Pygame display window required
- Runs in CI/CD pipelines
- Fast execution (~0.02s for all 11 tests)

### Pygame Mocking
- `pygame.key.get_pressed()` fully mocked
- `pygame.Rect` with AABB collision detection
- All display/event functions mocked

### Test Isolation
- Each test resets key state
- No cross-test contamination
- Session-scoped mock for performance

---

## Troubleshooting

### Tests Not Discovered
```bash
# Ensure pytest is installed
pip install pytest pytest-mock

# Check test discovery
pytest --collect-only
```

### Import Errors
```bash
# Verify src path is added (done in conftest.py)
# Or run from project root
cd /home/alexandre/historico
pytest tests/ -v
```

### Pygame Display Errors
- Should not occur — mocks prevent display init
- If error persists, check `conftest.py` `mock_pygame` fixture

---

## Next Steps

### Extend Test Coverage
- **Shooting mechanics**: Test projectile creation and direction
- **Network**: Mock network client and test movement updates
- **Rendering**: Test hitbox and player rendering (if needed)
- **Edge cases**: Simultaneous collisions, rapid key presses

### Integration Tests
- End-to-end gameplay scenarios
- Multi-player interactions
- Server-client communication

### CI/CD
Add to `.github/workflows/test.yml`:
```yaml
- name: Run tests
  run: |
    source .venv/bin/activate
    pytest tests/ -v --cov=src
```

---

## Dependencies

- `pytest>=9.0`
- `pytest-mock>=3.15`
- Python 3.8+

Installed in virtual environment at `.venv/`

---

**Test infrastructure created on:** November 16, 2025
**All 11 movement tests passing ✓**
