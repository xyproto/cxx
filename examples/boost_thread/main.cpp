#include <boost/chrono.hpp>
#include <boost/thread.hpp>
#include <iostream>

void wait(int seconds) { boost::this_thread::sleep_for(boost::chrono::seconds { seconds }); }

void thread()
{
    for (int i = 0; i < 5; ++i) {
        wait(1);
        std::cout << i << '\n';
    }
}

int main()
{
    boost::thread t { thread };
    t.join();
}
