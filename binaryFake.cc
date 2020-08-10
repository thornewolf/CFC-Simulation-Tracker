// binaryFake.cc
#include <iostream>
#include <chrono>
#include <thread>

int main() {
    int userInput[10];
    int t;
    for (int i = 0; i < 10; ++i) {
        std::cin >> t;
        userInput[i] = t;
    }
    for (int i = 0; i < 10; ++i) {
        std::cout << "This is iteration " << i << " with value " << userInput[i] << std::endl;
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    std::cout << std::endl;
    return 0;
}
