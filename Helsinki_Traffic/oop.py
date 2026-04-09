class Dog: 
    def __init__(self, name, age):
        self.name = name
        self.age = age
    def bark(self):
        print(f"{self.name} says Woo")



if __name__ == "__main__":
    dog = Dog("Tomy", 10).bark()
