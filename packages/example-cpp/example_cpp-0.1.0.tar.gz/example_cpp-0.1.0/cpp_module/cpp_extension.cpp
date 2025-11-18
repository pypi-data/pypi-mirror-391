#include <pybind11/pybind11.h>
#include <string>
#include <vector>
#include <algorithm>

// 1. 一个简单的C++函数
int add(int a, int b) {
    return a + b;
}

// 2. 一个C++类
class TextProcessor {
public:
    TextProcessor(const std::string& name) : name_(name) {}

    std::string to_upper(const std::string& input) {
        std::string result = input;
        std::transform(result.begin(), result.end(), result.begin(), ::toupper);
        return result;
    }

    void set_name(const std::string& name) { name_ = name; }
    std::string get_name() const { return name_; }

private:
    std::string name_;
};

// 3. 使用pybind11创建Python模块
namespace py = pybind11;

PYBIND11_MODULE(cpp_extension, m) {
    m.doc() = "A simple example module built with pybind11";

    // 暴露函数
    m.def("add", &add, "A function that adds two numbers");

    // 暴露类
    py::class_<TextProcessor>(m, "TextProcessor")
        .def(py::init<const std::string&>())
        .def("to_upper", &TextProcessor::to_upper)
        .def_property("name", &TextProcessor::get_name, &TextProcessor::set_name);
}