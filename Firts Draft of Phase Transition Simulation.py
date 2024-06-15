import pygame
import random
import math

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
ATOM_RADIUS = 5
SOLID_COLOR = (255, 255, 255)
LIQUID_COLOR = (0, 255, 0)
GAS_COLOR = (0, 0, 255)
SOLID_TEMP = 100  # Temperature threshold for solid-liquid transition
LIQUID_TEMP = 200  # Temperature threshold for liquid-gas transition
NUM_ATOMS = int(1.2 * 400)  # Number of atoms in the lattice increased by 20%
RESTORATION_FORCE = 0.001  # Force applied to restore atoms to their initial positions
SOLID_VIBRATION_AMPLITUDE = 0.05  # Amplitude of jittering in solid state
RESTORATION_TIME = 60  # Time in frames for the restoration transition

class Atom:
    def __init__(self, x, y, radius, color, state, initial_pos):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.state = state
        self.initial_pos = initial_pos
        self.restoring = False
        self.frames_restored = 0

    def update(self, temp):
        if self.state == 'Solid':
            self.jitter(temp)
        elif self.state == 'Liquid':
            if self.restoring:
                self.restore_to_initial_pos()
                self.frames_restored += 1
                if self.frames_restored >= RESTORATION_TIME:
                    self.restoring = False
            else:
                self.move(temp)
        else:
            self.move(temp)

    def jitter(self, temp):
        amplitude = SOLID_VIBRATION_AMPLITUDE * math.sqrt(temp)
        self.x = random.uniform(self.initial_pos[0] - amplitude, self.initial_pos[0] + amplitude)
        self.y = random.uniform(self.initial_pos[1] - amplitude, self.initial_pos[1] + amplitude)

    def move(self, temp):
        speed = 0.5 + temp / 200
        self.x += random.uniform(-speed, speed)
        self.y += random.uniform(-speed, speed)

    def restore_to_initial_pos(self):
        dx = self.initial_pos[0] - self.x
        dy = self.initial_pos[1] - self.y
        self.x += dx * RESTORATION_FORCE
        self.y += dy * RESTORATION_FORCE

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


def create_atoms_solid(num_atoms):
    atoms = []
    spacing = 2 * ATOM_RADIUS
    side_length = int(math.sqrt(num_atoms))
    lattice_size = spacing * side_length
    start_x = (WIDTH - lattice_size) / 2
    start_y = (HEIGHT - lattice_size) / 2

    for row in range(side_length):
        for col in range(side_length):
            x = start_x + col * spacing + random.uniform(-ATOM_RADIUS, ATOM_RADIUS)
            y = start_y + row * spacing + random.uniform(-ATOM_RADIUS, ATOM_RADIUS)
            initial_pos = (x, y)
            atom = Atom(x, y, ATOM_RADIUS, SOLID_COLOR, 'Solid', initial_pos)
            atoms.append(atom)

    return atoms


def create_atoms_liquid(atoms):
    for atom in atoms:
        atom.state = 'Liquid'
        atom.color = LIQUID_COLOR

    return atoms


def create_atoms_gas(atoms):
    for atom in atoms:
        atom.state = 'Gas'
        atom.color = GAS_COLOR

    return atoms


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Phase Transitions Simulation")
    clock = pygame.time.Clock()

    atoms = create_atoms_solid(NUM_ATOMS)
    current_temp = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        # Update and draw atoms
        for atom in atoms:
            atom.update(current_temp)
            atom.draw(screen)

        # Display temperature
        font = pygame.font.Font(None, 24)
        temp_text = font.render("T: {} K".format(current_temp), True, (255, 255, 255))
        screen.blit(temp_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

        # Increase temperature on key press
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            current_temp += 1
        if keys[pygame.K_DOWN]:
            current_temp -= 1

        # Check temperature range for state transitions
        if current_temp <= SOLID_TEMP:
            for atom in atoms:
                atom.state = 'Solid'
                atom.color = SOLID_COLOR
        elif current_temp <= LIQUID_TEMP:
            atoms = create_atoms_liquid(atoms)
        else:
            atoms = create_atoms_gas(atoms)

            # Start the restoration transition when transitioning from liquid to solid
            if current_temp <= SOLID_TEMP + 1:
                for atom in atoms:
                    atom.restoring = True
                    atom.frames_restored = 0

    pygame.quit()


if __name__ == '__main__':
    main()
