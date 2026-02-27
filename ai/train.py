#!/usr/bin/env python3
"""PVZ AI Training - Simple 1000 episodes"""

import random, time, json, threading

TOTAL = 1000
current = [0]
scores = []
best = [0]
genes = {'sun': 1.0, 'def': 1.0, 'row': 1.0, 'wall': 1.0, 'aggro': 1.0}

def episode(g):
    sun, wave, level = 350, 1, 1
    grid = [[None]*5 for _ in range(9)]
    zombies = []
    plants = []
    
    for step in range(300):
        # Spawn
        if step % 25 == 0 and len(zombies) < 3 + wave:
            row = random.randint(0, 4)
            zombies.append([row, 120, 800])
        
        # AI
        actions = []
        if sun >= 50:
            for c in range(2):
                for r in range(5):
                    if grid[c][r] is None:
                        actions.append(('sf', c, r))
                        break
                break
        if sun >= 100:
            for c in range(2, 6):
                for r in range(5):
                    if grid[c][r] is None:
                        actions.append(('ps', c, r))
                        break
                break
        
        actions.append(('w',))
        
        # Score
        best = actions[0]
        best_score = -999
        
        for a in actions:
            s = 0
            if a[0] == 'sf':
                s = 50 * genes['sun'] + (2 - a[1]) * 10
            elif a[0] == 'ps':
                row = a[2]
                s = 100 * genes['row']
                if any(z[0] == row for z in zombies):
                    s *= 2
                s -= abs(4 - a[1]) * 5
            elif a[0] == 'wn':
                s = 40 * genes['wall'] + a[1] * 5
            s += genes['aggro'] * 10
            
            if s > best_score:
                best_score = s
                best = a
        
        # Execute
        if best[0] == 'w':
            pass
        else:
            _, c, r = best
            if best[0] == 'sf':
                grid[c][r] = [80, 'sunflower']
                sun -= 50
                plants.append([c, r, 80, 'sunflower'])
            elif best[0] == 'ps':
                grid[c][r] = [100, 'peashooter']
                sun -= 100
                plants.append([c, r, 100, 'peashooter'])
            elif best[0] == 'wn':
                grid[c][r] = [400, 'wallnut']
                sun -= 50
                plants.append([c, r, 400, 'wallnut'])
        
        # Zombies
        for z in zombies[:]:
            z[1] -= 0.35
            
            # Attack
            for c in range(9):
                for r in range(5):
                    for p in plants:
                        if p[1] == c and p[0] == r:
                            if abs(z[1] - (120 + c * 80 + 40)) < 30:
                                p[2] -= 1.5
            
            # Peashooter
            for p in plants:
                if p[3] == 'peashooter':
                    if z[0] == p[1] and z[1] > 120 + p[0] * 80:
                        z[2] -= 25
                        if z[2] <= 0:
                            score += 5
        
        # Cleanup
        zombies = [z for z in zombies if z[2] > 0]
        plants = [p for p in plants if p[2] > 0]
        
        # Game over?
        for z in zombies:
            if z[1] < 100:
                return -100
        
        # Wave
        if step % 25 == 0 and len(zombies) == 0:
            wave += 1
            score += 5
            if wave > 5:
                level += 1
                wave = 1
                score += 10
        
        return (level - 1) * 5 + wave

def display():
    while current[0] < TOTAL:
        time.sleep(2)
        ep = current[0]
        
        if scores:
            avg = sum(scores[-100:]) / min(len(scores), 100)
            best = max(scores)
        else:
            avg = best = 0
        
        pct = (ep / TOTAL) * 100
        bar = '[' + '=' * int(pct / 2) + ' ' * (50 - int(pct / 2)) + ']'
        
        print(f"\r{bar} {ep}/{TOTAL} ({pct:.0f}%) | Avg: {avg:.1f} | Best: {best} | "
              f"{time.strftime('%H:%M:%S')}", end='', flush=True)
        
        if ep % 100 == 0 and ep > 0:
            print(f"\n{'='*55}\nEp {ep-99}-{ep}:\n")
            recent = scores[-100:]
            print(f"Avg: {sum(recent)/len(recent):.1f}")
            print(f"Best: {max(recent)}")
            print(f"Genes: {genes}")
            
            with open('result.json', 'w') as f:
                json.dump({'episode': ep, 'best': best, 'genes': genes}, f)
        
        if ep >= TOTAL:
            print(f"\nDone! Best: {best[0]}")

# Train
thread = threading.Thread(target=display, daemon=True)
thread.start()

for i in range(TOTAL):
    sc = episode(genes)
    scores.append(sc)
    current[0] = i + 1
    
    # Evolve every 150
    if i > 0 and i % 150 == 0:
        # Mutation
        k = random.choice(list(genes.keys()))
        genes[k] *= random.uniform(0.85, 1.15)
        print(f"\nEvolution at {i}: {k} -> {genes[k]:.3f}")

thread.join()

print(f"\nFinal: {best[0]}")
print(f"Avg: {sum(scores)/len(scores):.1f}")
