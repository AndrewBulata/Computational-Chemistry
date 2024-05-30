import pygame
import random
import math

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
ATOM_RADIUS = 5
SOLID_COLOR = (255, 255, 255) #Colour = white
LIQUID_COLOR = (0, 255, 0)
GAS_COLOR = (0, 0, 255)
SOLID_TEMP = 200  # Melting point of Xenon
LIQUID_TEMP = 211  # Boiling point of Xenon
NUM_ATOMS = int(1.2 * 400)  # Number of atoms in the lattice increased by 20%
XENON_SHOMATE = [29.02, 0.0296, -0.0000532]  # Shomate polynomial coefficients for Xenon (J/(mol·K), J/(mol·K^2), J/(mol·K^3))

class Atom:
    def __init__(self, x, y, radius, color, state, initial_pos):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.state = state
        self.initial_pos = initial_pos
        self.speed = 0.0

    def update(self, temp):
        if self.state == 'Solid':
            self.jitter(temp)
        elif self.state == 'Liquid':
            self.move(temp)
        elif self.state == 'Gas':
            self.move_gas(temp)

    def jitter(self, temp):
        amplitude = 0.1 * math.sqrt(temp)
        self.x = self.initial_pos[0] + random.uniform(-amplitude, amplitude)
        self.y = self.initial_pos[1] + random.uniform(-amplitude, amplitude)
        self.x = max(self.radius, min(self.x, WIDTH - self.radius))
        self.y = max(self.radius, min(self.y, HEIGHT - self.radius))

    def move(self, temp):
        # Calculate speed based on temperature
        speed = 0.5 + temp / 200
        self.x += random.uniform(-speed, speed)
        self.y += random.uniform(-speed, speed)
        self.x = max(self.radius, min(self.x, WIDTH - self.radius))
        self.y = max(self.radius, min(self.y, HEIGHT - self.radius))

    def move_gas(self, temp):
        # Calculate speed using Maxwell-Boltzmann distribution
        mean_speed = math.sqrt(2 * temp)
        if temp <= LIQUID_TEMP:
            speed_range = mean_speed / 2  # Proportion of particles with speeds outside this range decreases as temp increases
        else:
            speed_range = mean_speed / 4  # Smaller speed range for higher temperatures
        self.speed = random.uniform(mean_speed - speed_range, mean_speed + speed_range)
        angle = random.uniform(0, 2 * math.pi)
        vx = self.speed * math.cos(angle)
        vy = self.speed * math.sin(angle)
        self.x += vx
        self.y += vy
        self.x = max(self.radius, min(self.x, WIDTH - self.radius))
        self.y = max(self.radius, min(self.y, HEIGHT - self.radius))

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
            x = start_x + col * spacing
            y = start_y + row * spacing
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


def calculate_entropy(temp):
    a, b, c = XENON_SHOMATE
    entropy = math.log(temp + 1) * (a + b * temp + c / (temp ** 2 + 1))
    return entropy


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Phase Transitions Simulation 4")
    clock = pygame.time.Clock()

    atoms = create_atoms_solid(NUM_ATOMS)
    current_temp = 0
    entropy_value = calculate_entropy(current_temp)

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
        temp_font = pygame.font.Font(None, 24)
        temp_text = temp_font.render("T: {} K".format(current_temp), True, (255, 255, 255))
        screen.blit(temp_text, (10, 10))

        # Display entropy
        entropy_font = pygame.font.Font(None, 24)
        entropy_text = entropy_font.render("S: {:.2f} J/(mol·K)".format(entropy_value), True, (255, 255, 255))
        screen.blit(entropy_text, (10, 40))

        pygame.display.flip()
        clock.tick(FPS)

        # Increase/decrease temperature on key press
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            current_temp += 1
            entropy_value = calculate_entropy(current_temp)
        if keys[pygame.K_DOWN]:
            current_temp -= 1
            entropy_value = calculate_entropy(current_temp)

        # Check temperature range for state transitions
        if current_temp <= SOLID_TEMP:
            atoms = create_atoms_solid(NUM_ATOMS)
        elif current_temp <= LIQUID_TEMP:
            atoms = create_atoms_liquid(atoms)
        else:
            atoms = create_atoms_gas(atoms)

    pygame.quit()


if __name__ == '__main__':
    main()
