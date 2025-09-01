#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>
#include "solver.h"

namespace py = pybind11;

PYBIND11_MODULE(rummikub_solver, m) {
    m.doc() = "C++ solver for Rummikub-like game logic";

    // Bindowanie enuma TileColor
    py::enum_<TileColor>(m, "TileColor")
        .value("Red", TileColor::Red)
        .value("Blue", TileColor::Blue)
        .value("Yellow", TileColor::Yellow)
        .value("Black", TileColor::Black)
        .value("Joker", TileColor::Joker)
        .export_values();

    // Bindowanie klasy Tile
    py::class_<Tile>(m, "Tile")
        .def(py::init<int, TileColor>())
        .def_readwrite("number", &Tile::number)
        .def_readwrite("color", &Tile::color)
        .def("__repr__", [](const Tile &t) { // ZMIANA: Usunięto `[&]`
            if (t.color == TileColor::Joker) return std::string("Joker");
            std::string color_str;
            switch(t.color) {
                case TileColor::Red: color_str = "R"; break;
                case TileColor::Blue: color_str = "B"; break;
                case TileColor::Yellow: color_str = "Y"; break;
                case TileColor::Black: color_str = "K"; break;
                default: color_str = "?";
            }
            return color_str + std::to_string(t.number);
        })
        .def(py::self < py::self);


    // Bindowanie głównej funkcji
    m.def("find_all_valid_moves", &find_all_valid_moves_cpp,
        "Finds all valid moves (new table layouts)",
        py::arg("hand"),
        py::arg("table"),
        py::arg("first_only") = false);

    // Bindowanie nowej funkcji
    m.def("pre_filter_unplayable_tiles", &pre_filter_unplayable_tiles_cpp,
        "Filters out tiles from hand that cannot be part of any meld with current table and hand.",
        py::arg("hand"),
        py::arg("table"));

    // Zmodyfikowane bindowanie
    m.def("possible_moves", &possible_moves_cpp,
        "Returns all possible new table setups with used tiles",
        py::arg("hand"),
        py::arg("table"));
}