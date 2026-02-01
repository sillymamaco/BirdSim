import pygame as p
import random
import webbrowser

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720

class Bird:
    def __init__(self, x, y, images, is_leader=False):
        self.pos = p.math.Vector2(x, y)
        self.speed = p.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * 2
        self.acc = p.math.Vector2(0, 0)
        self.images = [p.transform.scale(img, (32, 32)) for img in images]
        self.frame = 0
        self.is_leader = is_leader
        self.max_speed = 2.0

    def apply_force(self, force):
        self.acc += force

    def update(self, birds):
        if not self.is_leader:
            sep_dist = 65    #stay together
            hard_radius = 28 #avoid overlap
            steer = p.math.Vector2(0, 0)
            avg_p = p.math.Vector2(0, 0)
            count = 0
            
            for o in birds:
                if o != self:
                    d = self.pos.distance_to(o.pos)
                    
                    if d < hard_radius:
                        push = (self.pos - o.pos)
                        if push.length() == 0: #move away randomly if they are on top of each other
                            push = p.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                        self.pos += push.normalize() * 2
                        self.speed.reflect_ip(push.normalize())
                    
                    elif d < sep_dist: #go with flock
                        diff = (self.pos - o.pos).normalize() / (d / sep_dist)**2
                        steer += diff
                        
                    if d < 180:
                        avg_p += o.pos
                        count += 1
            
            if steer.length() > 0:
                self.apply_force(steer.normalize() * 1.5)
            if count > 0:
                self.apply_force(((avg_p / count) - self.pos) * 0.005)
            self.apply_force((birds[0].pos - self.pos) * 0.012)
        else:
            if random.random() < 0.05:
                self.speed.rotate_ip(random.uniform(-20, 20))

        self.speed += self.acc
        if self.speed.length() > self.max_speed:
            self.speed.scale_to_length(self.max_speed)
        
        self.pos += self.speed
        self.acc *= 0
        self.frame = (self.frame + 0.1) % len(self.images) #wing movement

        margin = 35 #stay within bounds
        if self.pos.x <= margin or self.pos.x >= SCREEN_WIDTH - margin: self.speed.x *= -1
        if self.pos.y <= margin or self.pos.y >= SCREEN_HEIGHT - margin: self.speed.y *= -1
        self.pos.x = max(margin, min(self.pos.x, SCREEN_WIDTH - margin))
        self.pos.y = max(margin, min(self.pos.y, SCREEN_HEIGHT - margin))

    def draw(self, surface, show_dots):
        if show_dots:
            color = (104, 76, 61) if self.is_leader else (0, 0, 0)
            p.draw.circle(surface, color, (int(self.pos.x), int(self.pos.y)), 6)
        else:
            img = self.images[int(self.frame)]
            rect = img.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            surface.blit(img, rect)

class Simulation:
    def __init__(self):
        p.init()
        # Fullscreen + Scaled for Wayland support
        self.screen = p.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), p.FULLSCREEN | p.SCALED)
        self.clock = p.time.Clock()
        self.state = "menu"
        self.running = True
        self.show_dots = False
        self.font = p.font.Font("PressStart2P-Regular.ttf", 30)
        self.bird_imgs = [p.image.load(f"birdo{i}.png").convert_alpha() for i in range(1, 6)]
        
        # High quality backgrounds scaled once
        self.backgrounds = {}
        for k in ["menu", "simulation", "explanation", "warning"]:
            img = p.image.load(f"{k}.png").convert()
            self.backgrounds[k] = p.transform.smoothscale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            
        self.birds = []
        self.url = "https://www.discoverwildlife.com/animal-facts/birds/how-flocks-of-birds-are-able-to-fly-close-together"

    def handle_events(self):
        for e in p.event.get():
            if e.type == p.QUIT: self.running = False
            if e.type == p.KEYDOWN:
                if e.key == p.K_TAB: self.state = "menu"
                if e.key == p.K_a: self.state = "explanation"
                if e.key == p.K_SPACE: self.show_dots = not self.show_dots
                if e.key == p.K_b: 
                    self.state = "simulation"
                    if not self.birds: self.birds.append(Bird(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, self.bird_imgs, True))
                if e.key == p.K_e and len(self.birds) < 20:
                    self.birds.append(Bird(random.randint(50, SCREEN_WIDTH-50), random.randint(50, SCREEN_HEIGHT-50), self.bird_imgs))
                elif e.key == p.K_e: self.state = "warning"
                if e.key == p.K_x: self.state = "simulation"
                if e.key == p.K_ESCAPE: self.running = False
                if e.type == p.MOUSEBUTTONDOWN and self.state == "explanation":
                    webbrowser.open(self.url)
                # In Simulation.run()
                
    def run(self):
        while self.running:
            # Draw the background for the current state
            self.handle_events()
            if self.state in ["simulation", "warning"]:
                for b in self.birds: b.update(self.birds)
            bg=self.backgrounds.get(self.state, self.backgrounds["menu"])
            self.screen.blit(bg, (0, 0))
            if self.state == "explanation":
                lines = [
                    "BirdSim is an interactive ",
                    "app simulating flock ",
                    "movement, inspired by ",
                    "nature as in the link",
                    "below.",
                    "",
                    "ORIGINS",
                    "Made by sillymamaco",
                    "Bird sprites by Alfred",
                    "Idea by sillymamaco ",
                    "and two friends",
                    "",
                    "Press Esc to close the app",
                    "and Tab to go back ",
                    "to the menu!"
                ]

                for i, line in enumerate(lines):
                    text_surf = self.font.render(line, True, (82, 75, 36)) 
                    self.screen.blit(text_surf, (250, 135 + (i * 35)))
            
            elif self.state in ["simulation", "warning"]:
                for b in self.birds: b.draw(self.screen, self.show_dots)
                count_txt = self.font.render(str(len(self.birds)), True, (82, 75, 36))
                self.screen.blit(count_txt, (1100, 350))
                if self.state == "warning":
                    lines ="BIRD OVERLOAD!", "AAAAH NO MORE BIRDS!!!" 
                    for i, line in enumerate(lines):   
                        warning = self.font.render(line, True, (172, 50, 50))
                        self.screen.blit(warning, (200 - ( i *35), 100 + (i * 35)))      
            p.display.flip()
            self.clock.tick(60)
    p.quit()

if __name__ == "__main__":
    Simulation().run()