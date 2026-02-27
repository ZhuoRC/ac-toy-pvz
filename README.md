# Plants vs Zombies - Doodle Edition 🌻🧟

A hand-drawn style Plants vs Zombies clone in Python/Pygame.

## 🚀 Quick Start

```bash
pip install pygame
python src/pvz_game.py
```

## 📁 Structure

```
├── src/              # Main game
│   └── pvz_game.py   # Run this!
├── ai/               # AI training
│   ├── train.py      # Training script
│   ├── pvz_learning_ai.py
│   └── pvz_qlearning.py
├── docs/             # Documentation
├── assets/           # Images/sounds (future)
└── README.md
```

## 🌱 Plants

| Plant | Cost | Ability |
|-------|------|---------|
| 🌻 Sunflower | 50 | Produces sun |
| 🌱 Peashooter | 100 | Shoots peas |
| 🔫 Repeater | 200 | 2x damage! |
| 🌰 Wall-nut | 50 | 400 HP shield |

## 🧟 Zombies

| Zombie | HP | Speed |
|--------|-------|-------|
| Normal | 120 | 1.0x |
| 📐 Conehead | 280 | 1.0x |
| 🏈 Football | 600 | 1.7x |

## 🎯 Controls

- **1/2/3/4** - Select plant
- **Click** - Place plant/Collect sun
- **P** - Pause | **R** - Restart | **A** - AI mode

## 🤖 AI Training

```bash
python ai/train.py
```

## 📊 Features

- ✅ 5 waves, Full HD 1920x1080
- ✅ 15-column battlefield
- ✅ Hand-drawn doodle art
- ✅ AI vs AI modes

Built with Python & Pygame 🐍🎮
