import pygame, sys, os, json, random, math

BASE_W, BASE_H = 800, 650
CONFIG_FILE = "config.json"
SAVE_FILE = "save.json"

def load_config():
    default = {"width": BASE_W, "height": BASE_H, "fullscreen": False, "fps": 60}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                cfg = json.load(f)
            for k,v in default.items():
                if k not in cfg:
                    cfg[k] = v
            return cfg
        except:
            return default
    return default

def load_save():
    default = {"highscore":0}
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE,"r") as f:
                s = json.load(f)
            if "highscore" not in s:
                s["highscore"] = 0
            return s
        except:
            return default
    return default

def save_config(cfg):
    try:
        with open(CONFIG_FILE,"w") as f:
            json.dump(cfg,f)
    except:
        pass

def save_save(s):
    try:
        with open(SAVE_FILE,"w") as f:
            json.dump(s,f)
    except:
        pass

cfg = load_config()
saved = load_save()
FPS = int(cfg.get("fps",60))
TELA_CHEIA = bool(cfg.get("fullscreen",False))
TARGET_W, TARGET_H = int(cfg.get("width",BASE_W)), int(cfg.get("height",BASE_H))

pygame.init()
pygame.display.set_caption("ILUSION")
def create_screen():
    flags = pygame.FULLSCREEN if TELA_CHEIA else 0
    if TELA_CHEIA:
        return pygame.display.set_mode((0,0), flags)
    return pygame.display.set_mode((TARGET_W, TARGET_H), flags)
screen = create_screen()
clock = pygame.time.Clock()

img_folder = "img"
fundo_img = pygame.image.load(os.path.join(img_folder,"pista.png")).convert()
car_path = os.path.join(img_folder,"car.png") if os.path.exists(os.path.join(img_folder,"car.png")) else os.path.join(img_folder,"car01.png")
car_src = pygame.image.load(car_path).convert_alpha()
obstacle01_src = pygame.image.load(os.path.join(img_folder,"obstacle01.png") if os.path.exists(os.path.join(img_folder,"obstacle01.png")) else os.path.join(img_folder,"inimigo01.png")).convert_alpha()
obstacle02_src = pygame.image.load(os.path.join(img_folder,"obstacle02.png") if os.path.exists(os.path.join(img_folder,"obstacle02.png")) else os.path.join(img_folder,"inimigo02.png")).convert_alpha()
obstacle03_src = pygame.image.load(os.path.join(img_folder,"obstacle03.png") if os.path.exists(os.path.join(img_folder,"obstacle03.png")) else os.path.join(img_folder,"inimigo03.png")).convert_alpha()
obstacles_src = [obstacle01_src, obstacle02_src, obstacle03_src]

def choose_font():
    choices = ["Orbitron","Montserrat","Arial","Verdana","DejaVuSans"]
    for c in choices:
        f = pygame.font.match_font(c)
        if f:
            return f
    return None
FONT_NAME = choose_font()
def make_font(sz):
    if FONT_NAME:
        return pygame.font.Font(FONT_NAME, sz)
    return pygame.font.Font(None, sz)
def render_text(s, sz, color):
    return make_font(sz).render(str(s), True, color)

def create_assets():
    global fundo_base, car, obstacles, car_w, car_h, lanes
    fundo_base = pygame.transform.scale(fundo_img, (BASE_W, BASE_H))
    car_w = int(BASE_W * 0.1)
    car_h = int(car_src.get_height() * (car_w / car_src.get_width()))
    car = pygame.transform.scale(car_src, (car_w, car_h))
    obstacles = [pygame.transform.scale(i, (car_w, car_h)) for i in obstacles_src]
    lanes = [
        int(BASE_W * 0.315) - car_w // 2,
        int(BASE_W * 0.435) - car_w // 2,
        int(BASE_W * 0.555) - car_w // 2,
        int(BASE_W * 0.675) - car_w // 2
    ]
create_assets()

def get_supported_modes():
    modes = pygame.display.list_modes()
    common = [(320,240),(640,480),(1280,720),(1920,1080),(2560,1440),(3840,2160)]
    final = []
    if modes:
        native = modes[0]
        if native not in final:
            final.append(native)
    for r in common:
        if r not in final:
            final.append(r)
    return final
display_modes = get_supported_modes()

def set_window(w,h,fullscreen):
    global screen, TARGET_W, TARGET_H, TELA_CHEIA
    TARGET_W, TARGET_H = int(w), int(h)
    TELA_CHEIA = bool(fullscreen)
    cfg["widther"], cfg["height"], cfg["fullscreen"] = TARGET_W, TARGET_H, TELA_CHEIA
    save_config(cfg)
    flags = pygame.FULLSCREEN if TELA_CHEIA else 0
    if TELA_CHEIA:
        screen = pygame.display.set_mode((0,0), flags)
    else:
        screen = pygame.display.set_mode((TARGET_W, TARGET_H), flags)

def toggle_fullscreen():
    global TELA_CHEIA, screen
    TELA_CHEIA = not TELA_CHEIA
    cfg["fullscreen"] = TELA_CHEIA
    save_config(cfg)
    flags = pygame.FULLSCREEN if TELA_CHEIA else 0
    if TELA_CHEIA:
        screen = pygame.display.set_mode((0,0), flags)
    else:
        screen = pygame.display.set_mode((TARGET_W, TARGET_H), flags)

def draw_base_to_screen(base_surf):
    real_w, real_h = screen.get_size()
    scale = min(real_w / BASE_W, real_h / BASE_H)
    sw = int(BASE_W * scale)
    sh = int(BASE_H * scale)
    scaled = pygame.transform.scale(base_surf, (sw, sh))
    ox = (real_w - sw)//2
    oy = (real_h - sh)//2
    screen.blit(scaled, (ox, oy))
    return ox, oy, scale

def draw_base_preview():
    real_w, real_h = screen.get_size()
    scale = min(real_w / BASE_W, real_h / BASE_H)
    sw = int(BASE_W * scale)
    sh = int(BASE_H * scale)
    ox = (real_w - sw)//2
    oy = (real_h - sh)//2
    return ox, oy, scale

def button(surface, rect, label, mouse_rel, mouse_pressed, focused=False):
    x,y,w,h = rect
    mx,my = mouse_rel
    inside = x <= mx <= x+w and y <= my <= y+h
    bg = (95,95,95) if inside or focused else (70,70,70)
    pygame.draw.rect(surface, bg, rect, border_radius=8)
    txt = render_text(label, 26, (245,245,245))
    surface.blit(txt, (x + 14, y + (h - txt.get_height())//2))
    clicked = inside and mouse_pressed and mouse_pressed[0]
    key_activate = focused and pygame.key.get_pressed()[pygame.K_RETURN]
    return clicked or key_activate

def centered_button(surface, cx, y, w, h, label, mouse_rel, mouse_pressed, focused=False):
    x = cx - w//2
    return button(surface, (x,y,w,h), label, mouse_rel, mouse_pressed, focused)

def draw_main_menu():
    sel = 0
    items = ["Start Game","Options","Quit"]
    while True:
        base = pygame.Surface((BASE_W, BASE_H))
        base.fill((18,18,18))
        title = render_text("ILUSION", 96, (255,255,255))
        base.blit(title, (BASE_W//2 - title.get_width()//2, 68))
        mouse_pos = pygame.mouse.get_pos()
        ox,oy,scale = draw_base_preview()
        rel_mouse = ((mouse_pos[0]-ox)/scale, (mouse_pos[1]-oy)/scale)
        mouse_pressed = pygame.mouse.get_pressed()
        for i,label in enumerate(items):
            focused = (i==sel)
            clicked = centered_button(base, BASE_W//2, 260 + i*90, 360, 64, label, rel_mouse, mouse_pressed, focused)
            if clicked:
                if label=="Start Game":
                    game_loop()
                    sel = 0
                    break
                if label=="Options":
                    options_loop()
                    sel = 0
                    break
                if label=="Quit":
                    pygame.quit(); sys.exit()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_DOWN:
                    sel = (sel + 1) % len(items)
                if e.key == pygame.K_UP:
                    sel = (sel - 1) % len(items)
                if e.key == pygame.K_RETURN:
                    if items[sel]=="Start Game":
                        game_loop()
                        sel = 0
                        break
                    if items[sel]=="Options":
                        options_loop()
                        sel = 0
                        break
                    if items[sel]=="Quit":
                        pygame.quit(); sys.exit()
                if e.key == pygame.K_F4:
                    toggle_fullscreen()
        draw_base_to_screen(base)
        mx,my = pygame.mouse.get_pos()
        pygame.mouse.set_visible(True)
        pygame.display.update()
        clock.tick(30)

def options_loop():
    res_list = display_modes
    native = pygame.display.Info()
    native_mode = (native.current_w, native.current_h)
    if native_mode not in res_list:
        res_list.insert(0, native_mode)
    sel_res = res_list.index((cfg.get("width",BASE_W),cfg.get("height",BASE_H))) if (cfg.get("width",BASE_W),cfg.get("height",BASE_H)) in res_list else 0
    fps_options = [30,60,75,120,240]
    sel_fps = fps_options.index(cfg.get("fps",60)) if cfg.get("fps",60) in fps_options else 1
    sel_index = 0
    items = ["resolution","fps","fullscreen","back"]
    while True:
        base = pygame.Surface((BASE_W, BASE_H))
        base.fill((22,22,22))
        base.blit(render_text("OPTIONS",64,(255,255,255)), (BASE_W//2 - 120, 40))
        mouse_pos = pygame.mouse.get_pos()
        ox,oy,scale = draw_base_preview()
        rel_mouse = ((mouse_pos[0]-ox)/scale, (mouse_pos[1]-oy)/scale)
        mouse_pressed = pygame.mouse.get_pressed()
        y0 = 150
        r_label = f"{res_list[sel_res][0]} x {res_list[sel_res][1]}"
        if button(base, (BASE_W//2 - 220, y0, 440, 56), f"Resolution: {r_label}", rel_mouse, mouse_pressed, sel_index==0):
            sel_res = (sel_res + 1) % len(res_list)
            w,h = res_list[sel_res]
            set_window(w,h,TELA_CHEIA)
            cfg["width"], cfg["height"] = w,h
            save_config(cfg)
        y0 += 90
        if button(base, (BASE_W//2 - 220, y0, 440, 56), f"FPS: {fps_options[sel_fps]}", rel_mouse, mouse_pressed, sel_index==1):
            sel_fps = (sel_fps + 1) % len(fps_options)
            FPS = fps_options[sel_fps]
            cfg["fps"] = FPS
            save_config(cfg)
        y0 += 90
        full_label = "On" if TELA_CHEIA else "Off"
        if button(base, (BASE_W//2 - 220, y0, 440, 56), f"Fullscreen: {full_label}", rel_mouse, mouse_pressed, sel_index==2):
            toggle_fullscreen()
            cfg["fullscreen"] = TELA_CHEIA
            save_config(cfg)
        y0 += 110
        if centered_button(base, BASE_W//2, y0, 300, 56, "Back", rel_mouse, mouse_pressed, sel_index==3):
            draw_main_menu()
            return
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_DOWN:
                    sel_index = (sel_index + 1) % len(items)
                if e.key == pygame.K_UP:
                    sel_index = (sel_index - 1) % len(items)
                if e.key == pygame.K_RETURN:
                    if items[sel_index]=="resolution":
                        sel_res = (sel_res + 1) % len(res_list)
                        w,h = res_list[sel_res]
                        set_window(w,h,TELA_CHEIA)
                        cfg["width"], cfg["height"] = w,h
                        save_config(cfg)
                    if items[sel_index]=="fps":
                        sel_fps = (sel_fps + 1) % len(fps_options)
                        FPS = fps_options[sel_fps]
                        cfg["fps"] = FPS; save_config(cfg)
                    if items[sel_index]=="fullscreen":
                        toggle_fullscreen(); cfg["fullscreen"]=TELA_CHEIA; save_config(cfg)
                    if items[sel_index]=="back":
                        draw_main_menu(); return
                if e.key == pygame.K_ESCAPE:
                    draw_main_menu(); return
                if e.key == pygame.K_F4:
                    toggle_fullscreen(); cfg["fullscreen"]=TELA_CHEIA; save_config(cfg)
        draw_base_to_screen(base)
        mx,my = pygame.mouse.get_pos()
        pygame.mouse.set_visible(True)
        pygame.display.update()
        clock.tick(30)

def pause_menu():
    sel = 0
    items = ["Resume","Main Menu","Quit"]
    while True:
        base = pygame.Surface((BASE_W, BASE_H))
        overlay = pygame.Surface((BASE_W, BASE_H))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        base.blit(overlay,(0,0))
        base.blit(render_text("PAUSED",72,(255,255,255)), (BASE_W//2 - 160, 120))
        mouse_pos = pygame.mouse.get_pos()
        ox,oy,scale = draw_base_preview()
        rel_mouse = ((mouse_pos[0]-ox)/scale, (mouse_pos[1]-oy)/scale)
        mouse_pressed = pygame.mouse.get_pressed()
        for i,label in enumerate(items):
            focused = (i==sel)
            clicked = centered_button(base, BASE_W//2, 280 + i*90, 380, 64, label, rel_mouse, mouse_pressed, focused)
            if clicked:
                if label=="Resume":
                    return
                if label=="Main Menu":
                    draw_main_menu()
                    return
                if label=="Quit":
                    pygame.quit(); sys.exit()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_DOWN:
                    sel = (sel+1)%len(items)
                if e.key == pygame.K_UP:
                    sel = (sel-1)%len(items)
                if e.key == pygame.K_RETURN:
                    if items[sel]=="Resume": return
                    if items[sel]=="Main Menu": draw_main_menu(); return
                    if items[sel]=="Quit": pygame.quit(); sys.exit()
                if e.key == pygame.K_ESCAPE:
                    return
                if e.key == pygame.K_F4:
                    toggle_fullscreen()
        draw_base_to_screen(base)
        mx,my = pygame.mouse.get_pos()
        pygame.mouse.set_visible(True)
        pygame.display.update()
        clock.tick(30)

def game_over_screen(score, is_new, initial_position=None, speed=None, elapsed_time=None, s_final=None):
    while True:
        base = pygame.Surface((BASE_W, BASE_H))
        base.fill((0,0,0))
        base.blit(render_text("GAME OVER",72,(255,50,50)), (BASE_W//2 - 212, 100))
        base.blit(render_text(f"Score: {int(score)}",40,(255,255,255)), (BASE_W//2 - 160, 217))
        base.blit(render_text(f"High Score: {int(saved.get('highscore',0))}",36,(255,215,0)), (BASE_W//2 - 160, 260))
        if is_new:
            base.blit(render_text("New High Score!",32,(0,200,100)), (BASE_W//2 - 120, 330))


        if initial_position is not None and speed is not None and elapsed_time is not None and s_final is not None:
            base.blit(render_text(f"S0 = {initial_position}", 22, (200,200,200)), (BASE_W//2 - 225, 330))
            base.blit(render_text(f"v = {speed:.3f} px/s", 22, (200,200,200)), (BASE_W//2 - 222, 347))
            base.blit(render_text(f"t = {elapsed_time:.2f} s", 22, (200,200,200)), (BASE_W//2 - 220, 365))
            base.blit(render_text(f"S = {s_final:.3f} px", 28, (180,255,180)), (BASE_W//2 - 224, 386))

        mouse_pos = pygame.mouse.get_pos()
        ox,oy,scale = draw_base_preview()
        rel_mouse = ((mouse_pos[0]-ox)/scale, (mouse_pos[1]-oy)/scale)
        mouse_pressed = pygame.mouse.get_pressed()

        if centered_button(base, BASE_W//2, 460, 380, 64, "Try Again", rel_mouse, mouse_pressed):
            return True
        if centered_button(base, BASE_W//2, 550, 380, 64, "Main Menu", rel_mouse, mouse_pressed):
            draw_main_menu(); return False
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F4:
                    toggle_fullscreen()
                if e.key == pygame.K_ESCAPE:
                    draw_main_menu(); return False
        draw_base_to_screen(base)
        mx,my = pygame.mouse.get_pos()
        pygame.mouse.set_visible(True)
        pygame.display.update()
        clock.tick(30)

def spawn_wave(in_list, dist_min, dist_max):
    num = random.choices([1,2,3], weights=[6,3,1])[0]
    chosen = random.sample(range(len(lanes)), num)
    y0 = -random.randint(dist_min, dist_max)
    chosen.sort()
    for c in chosen:
        img = random.choice(obstacles)
        in_list.append({"x": lanes[c], "y": y0, "img": img})
        y0 -= random.randint(320, 520)

def game_loop():
    global FPS, saved
    fundo_y1, fundo_y2 = 0, -BASE_H
    lane_idx = 1
    x = lanes[lane_idx]
    y = BASE_H - car_h - 20
    destino_x = x
    in_list = []
    score = 0.0
    speed = 13.0
    diff_timer = 0.0
    dist_min, dist_max = 900, 1500
    spawn_wave(in_list, dist_min, dist_max)
    running = True
    
    start_time = pygame.time.get_ticks()  
    
    while running:
        dt = clock.tick(FPS) / 60.0  
        diff_timer += dt
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pause_menu()
                if e.key == pygame.K_F4:
                    toggle_fullscreen()
                if e.key == pygame.K_LEFT and lane_idx > 0:
                    lane_idx -= 1
                    destino_x = lanes[lane_idx]
                if e.key == pygame.K_RIGHT and lane_idx < len(lanes)-1:
                    lane_idx += 1
                    destino_x = lanes[lane_idx]
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            y -= speed * dt * 4.0
        if keys[pygame.K_DOWN]:
            y += speed * dt * 4.0
        y = max(0, min(BASE_H - car_h, y)) 
        
        if abs(x - destino_x) > 2:
            x += (destino_x - x) * 0.35
        else:
            x = destino_x
        
        fundo_y1 += speed
        fundo_y2 += speed
        if fundo_y1 >= BASE_H: fundo_y1 = fundo_y2 - BASE_H
        if fundo_y2 >= BASE_H: fundo_y2 = fundo_y1 - BASE_H
        
        for o in in_list:
            o["y"] += speed + 2
        
        if all(o["y"] > BASE_H + 250 for o in in_list):
            spawn_wave(in_list, dist_min, dist_max)
        
        rect_player = pygame.Rect(x, y, car_w, car_h)
        collided = any(rect_player.colliderect(pygame.Rect(o["x"], o["y"], car_w, car_h)) for o in in_list)
        if collided:
            is_new = score > saved.get("highscore", 0)
            if is_new:
                saved["highscore"] = int(score)
                save_save(saved)
            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000.0
            initial_position = BASE_H - car_h - 20
            s_final = initial_position + speed * elapsed_time
            again = game_over_screen(score, is_new, initial_position, speed, elapsed_time, s_final)
            if again:
                return game_loop()
            else:
                return
        
        score += dt * (0.9 + (speed - 7.0) * 0.10)
        
        if diff_timer > 9.0 and speed < 13.0:
            diff_timer = 0.0
            speed = min(speed + 0.4, 13.0)
            dist_min = max(420, dist_min - 40)
            dist_max = max(520, dist_max - 60)
        
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000 
        initial_position = BASE_H - car_h - 20  
        position = y 
        formula_text = f"S = {initial_position} + {speed} * {elapsed_time:.2f}"
        
        base = pygame.Surface((BASE_W, BASE_H))
        base.blit(fundo_base, (0, fundo_y1))
        base.blit(fundo_base, (0, fundo_y2))
        
        for o in in_list:
            base.blit(o["img"], (o["x"], o["y"]))
        
        base.blit(car, (x, y))
        
        formula_surf = render_text(formula_text, 24, (255, 255, 255))
        base.blit(formula_surf, (12, BASE_H - 40))
        
        score_surf = render_text(f"Score: {int(score)}", 28, (255, 255, 255))
        base.blit(score_surf, (12, 10))
        
        draw_base_to_screen(base)
        
        mx, my = pygame.mouse.get_pos()
        pygame.mouse.set_visible(True)
        pygame.display.update()

set_window(TARGET_W, TARGET_H, TELA_CHEIA)
create_assets()
draw_main_menu()
