#include <Python.h>
#include <torch/script.h>

#include <iostream>
#include <memory>

int main(int argc, const char* argv[])
{
    if (argc != 2) {
        std::cerr << "usage: ./pytorch <path-to-exported-script-module>" << std::endl;
        return -1;
    }

    // Deserialize the ScriptModule from a file using torch::jit::load().
    std::shared_ptr<torch::jit::script::Module> module = torch::jit::load(argv[1]);

    assert(module != nullptr);

    std::cout << "ok" << std::endl;
}
