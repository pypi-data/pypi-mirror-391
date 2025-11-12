# from Data import Colors, TimeMode
import time
from logger_pauwels import Logger, Colors, TimeMode

hello_world = "Hello, world!"
long_text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed id libero a neque vulputate commodo in at est. Quisque ornare justo non metus interdum sodales. Nunc ornare augue sit amet metus bibendum, non laoreet orci pulvinar. Nam sapien nunc, posuere id vestibulum quis, viverra vitae massa. Nunc laoreet metus vitae porta molestie. Curabitur at orci nec dolor consequat maximus vel ut justo. Donec varius lorem at egestas condimentum. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Vivamus sodales pellentesque auctor. Aenean commodo justo sed libero ullamcorper maximus et in enim. Sed sed faucibus eros. Mauris sagittis, mauris sed venenatis blandit, erat ligula pharetra neque, quis blandit orci lectus vel nisl. Etiam nec eleifend orci. Pellentesque venenatis dolor vitae lorem porttitor, a finibus mauris dapibus. Donec rhoncus orci mi, at hendrerit sapien luctus ut. Cras malesuada semper nisl non tempus. Integer eu nibh eros. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Donec accumsan magna erat. Fusce pretium egestas aliquam. Pellentesque lectus justo, molestie ut rutrum eget, interdum convallis lectus. Quisque posuere ac libero ut aliquam. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Etiam et tincidunt lacus. Morbi nec libero vel lorem mattis pulvinar. Vivamus condimentum rhoncus porttitor. Morbi sit amet laoreet urna. Nam ullamcorper nisi nec odio elementum, porttitor vulputate orci ultricies. Phasellus ac lorem sit amet sem convallis pretium sit amet ac lorem. Sed et eros non sem rutrum dignissim. Quisque tortor lorem, ultricies vitae lectus vel, hendrerit mollis urna. Curabitur laoreet quam neque, in semper risus sollicitudin ac. Morbi nec turpis ante. Curabitur mollis sit amet tortor et cursus. In quis ligula et tortor congue pretium. Maecenas id pulvinar tellus. Nullam urna erat, placerat vitae ultricies sed, tincidunt et erat. Sed dapibus aliquam lacinia. Nullam tempor augue eu lorem rutrum, eget faucibus magna tempus. Vestibulum tristique felis sit amet leo mattis tincidunt. Sed eu augue faucibus, ultricies eros eget, eleifend eros. Nam scelerisque est et diam venenatis bibendum. Vivamus nec leo et urna molestie feugiat. Quisque lacinia lacus nec sapien ullamcorper, sodales interdum velit rhoncus. Donec id elit et nisi eleifend tincidunt fermentum vitae tellus. Aliquam nec ipsum sit amet urna ornare porta a eu dolor. Nullam sollicitudin tellus ante, non maximus tellus convallis ut. Sed sodales scelerisque diam eu interdum. Nam augue justo, hendrerit eget enim eget, vehicula maximus felis. Vivamus tristique, odio ut maximus posuere, sapien magna interdum ipsum, vitae maximus massa arcu a sem. Pellentesque nulla ante, auctor at justo eu, fringilla venenatis urna. Curabitur malesuada accumsan porttitor. Nam pretium augue sit amet maximus euismod. Vestibulum quis nulla eu urna porttitor pretium sit amet vel ex. Curabitur sed aliquam velit. Quisque lacinia a neque consectetur ultricies. Vivamus vitae faucibus est. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Aenean sem tellus, fermentum in fringilla ac, iaculis blandit magna. Maecenas luctus, nulla in finibus sollicitudin, velit elit ultrices leo, volutpat rutrum leo arcu et velit."""

l = Logger()

def test_short_rainbow():
    l.print_rainbow(hello_world)

def test_long_rainbow():
    l.print_rainbow(long_text)

def test_short_log():
    l.log(hello_world)

def test_red_log():
    l.print("I'm red !", Colors.RED)

def test_gray_scale_log():
    l.print("Black", Colors.BLACK)
    l.print("DARK GRAY", Colors.DARK_GRAY)
    l.print("GRAY", Colors.GRAY)
    l.print("LIGHT GRAY", Colors.LIGHT_GRAY)
    l.print("WHITE", Colors.WHITE)

def test_cadre():
    l.cadre("MON SUPER CADRE", padding=1)

def test_cadre_vert():
    l.cadre("MON SUPER CADRE VERT", padding=2, color=Colors.GREEN)

def test_section_jaune():
    l.section("Section Jaune", char=".", color=Colors.YELLOW)

def test_section_violet():
    l.section("Section Violette", char="*", color=Colors.PURPLE, padding=1, length=50)

def test_log():
    l.log("This is a log")

def test_warn():
    l.warn("This is a warning")

def test_error():
    l.error("This is an error")

def test_debug():
    l.debug("This is a debug")

def test_save():
    l.save()

def test_save_fail():
    l.save("tony/parker/tonton.log")

def test_chrono():
    l.start_timer()
    l.log("Debut du chrono")
    time.sleep(0.2)
    l.log("Attente 0.2 seconde")
    time.sleep(0.4)
    l.log("Attente 0.4 seconde")
    l.error("Meme indentation ?")
    l.stop_timer()
    l.log("Y'a plus de timer là normamalement")
    l.save()

def test_date():
    l.time_mode = TimeMode.DATE
    l.log("Tentative de date")
    time.sleep(0.3)
    l.error("C'est la meme indentation ?")

def test_time():
    l.time_mode = TimeMode.TIME
    l.log("Tentative de time")
    time.sleep(0.1)
    l.error("C'est la meme indentation ?")

def simulation_utilisation():
    l.init()
    time.sleep(0.1)
    l.log("On recupère les datas")
    time.sleep(0.2)
    l.warn("Attention, la liste est vide")
    time.sleep(0.1)
    l.log("Site créé")
    time.sleep(0.5)
    l.error("Pas d'accès internet")
    l.end()