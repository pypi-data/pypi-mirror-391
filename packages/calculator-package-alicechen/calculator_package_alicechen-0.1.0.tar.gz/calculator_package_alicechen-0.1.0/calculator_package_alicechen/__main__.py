from .calc_class import Calculator

def main():
    print("I'm in main!")
    print(Calculator().add(3,3))

# prevents code from running unintentionally
if __name__ == "__main__":
    main()
