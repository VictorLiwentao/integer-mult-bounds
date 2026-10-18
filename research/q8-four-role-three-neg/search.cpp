// SPDX-License-Identifier: Apache-2.0
// Exact four-role three-negative Q8 exclusion through length 7.
// Prepared by Wentao Li with substantial AI assistance.
#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>
#include <unordered_set>
#include <vector>

using State = std::array<std::uint32_t, 4>;

struct Factor {
    unsigned u, v, g;
};

struct Hash {
    std::size_t operator()(const State& state) const {
        std::size_t hash = 1469598103934665603ull;
        for (auto word : state) {
            hash ^= word;
            hash *= 1099511628211ull;
        }
        return hash;
    }
};

using Set = std::unordered_set<State, Hash>;
using Table = std::array<std::array<unsigned, 256>, 8>;

void require(bool ok, const std::string& message) {
    if (!ok) throw std::runtime_error(message);
}

unsigned group_product(unsigned left, unsigned right) {
    // Encoding: 1, z, i, zi, j, zj, k, zk. i*j=k and j*i=zk.
    const unsigned x = left >> 1, y = right >> 1;
    const unsigned neg = (left & 1U) ^ (right & 1U) ^
        static_cast<unsigned>((x != 0 && x == y) || (x == 2 && y == 1) ||
                              (x == 3 && y == 2) || (x == 1 && y == 3));
    return ((x ^ y) << 1) | neg;
}

Table multiplication_table() {
    Table table{};
    for (unsigned label = 0; label < 8; ++label)
        for (unsigned mask = 0; mask < 256; ++mask)
            for (unsigned basis = 0; basis < 8; ++basis)
                if ((mask >> basis) & 1U)
                    table[label][mask] ^= 1U << group_product(basis, label);
    return table;
}

State identity(unsigned roles) {
    State state{};
    for (unsigned role = 0; role < roles; ++role)
        state[role] = 1U << (8 * role);
    return state;
}

std::vector<Factor> alphabet(unsigned roles, bool inverse) {
    require(roles >= 1 && roles <= 4, "role limit");
    std::vector<Factor> factors;
    for (unsigned image = 1; image < (1U << roles); ++image)
        for (unsigned covector = 1; covector < (1U << roles); ++covector)
            if ((__builtin_popcount(image & covector) & 1) != 0)
                for (unsigned label : {2U, 4U})
                    factors.push_back({image, covector, label + unsigned(inverse)});
    return factors;
}

State apply_factor(State state, Factor factor, unsigned roles, const Table& table) {
    for (unsigned row = 0; row < roles; ++row) {
        unsigned support = 0;
        for (unsigned role = 0; role < roles; ++role)
            if ((factor.u >> role) & 1U)
                support ^= (state[row] >> (8 * role)) & 255U;
        const unsigned delta = support ^ table[factor.g][support];
        for (unsigned column = 0; column < roles; ++column)
            if ((factor.v >> column) & 1U)
                state[row] ^= delta << (8 * column);
    }
    return state;
}

State multiply_target(State state, const std::string& target, unsigned roles,
                      const Table& table) {
    require(target.size() == roles, "target width");
    for (unsigned row = 0; row < roles; ++row) {
        std::uint32_t mixed = 0;
        for (unsigned column = 0; column < roles; ++column) {
            const unsigned label = unsigned(target[column] - '0');
            require(label < 8, "target label");
            mixed |= table[label][(state[row] >> (8 * column)) & 255U] << (8 * column);
        }
        state[row] = mixed;
    }
    return state;
}

struct SearchResult {
    unsigned roles;
    std::string target;
    std::uint64_t inverse_ball;
    std::uint64_t prefix_ball;
    std::uint64_t candidates;
    std::uint64_t hits;
};

SearchResult meet(unsigned roles, unsigned left, unsigned right,
                  const std::string& target, const Table& table) {
    require(left == 3 && right == 4, "this certificate uses the 3+4 split");
    const auto inverse_factors = alphabet(roles, true);
    const auto forward_factors = alphabet(roles, false);
    Set inverse_seen{identity(roles)};
    std::vector<State> frontier{identity(roles)};
    inverse_seen.reserve(roles == 4 ? (1u << 23) : (1u << 17));
    for (unsigned depth = 0; depth < left; ++depth) {
        std::vector<State> next;
        next.reserve(frontier.size());
        for (const auto& state : frontier)
            for (auto factor : inverse_factors) {
                auto image = apply_factor(state, factor, roles, table);
                if (inverse_seen.insert(image).second) next.push_back(image);
            }
        frontier.swap(next);
    }
    Set wanted;
    wanted.reserve(inverse_seen.size() * 2);
    for (const auto& state : inverse_seen)
        wanted.insert(multiply_target(state, target, roles, table));

    Set prefix_seen{identity(roles)};
    prefix_seen.reserve(inverse_seen.bucket_count());
    std::vector<State> prefixes{identity(roles)};
    frontier.assign(1, identity(roles));
    for (unsigned depth = 0; depth < right - 1; ++depth) {
        std::vector<State> next;
        for (const auto& state : frontier)
            for (auto factor : forward_factors) {
                auto image = apply_factor(state, factor, roles, table);
                if (prefix_seen.insert(image).second) {
                    next.push_back(image);
                    prefixes.push_back(image);
                }
            }
        frontier.swap(next);
    }

    std::uint64_t hits = 0, candidates = 0;
    for (const auto& state : prefixes) {
        hits += wanted.count(state);
        ++candidates;
        for (auto factor : forward_factors) {
            hits += wanted.count(apply_factor(state, factor, roles, table));
            ++candidates;
        }
    }
    return {roles, target, inverse_seen.size(), prefixes.size(), candidates, hits};
}

std::uint64_t depth_ball(unsigned roles, unsigned depth, const Table& table) {
    const auto factors = alphabet(roles, false);
    Set seen{identity(roles)};
    std::vector<State> frontier{identity(roles)};
    seen.reserve(1u << 16);
    for (unsigned step_index = 0; step_index < depth; ++step_index) {
        std::vector<State> next;
        for (const auto& state : frontier)
            for (auto factor : factors) {
                auto image = apply_factor(state, factor, roles, table);
                if (seen.insert(image).second) next.push_back(image);
            }
        frontier.swap(next);
    }
    return seen.size();
}

int main() {
    try {
        const auto table = multiplication_table();
        // Associativity of all 512 triples, and factor-inverse law at four roles.
        for (unsigned a = 0; a < 8; ++a)
            for (unsigned b = 0; b < 8; ++b)
                for (unsigned c = 0; c < 8; ++c)
                    require(group_product(group_product(a, b), c) ==
                                group_product(a, group_product(b, c)),
                            "Q8 associativity");
        const auto factors = alphabet(4, false);
        require(factors.size() == 240, "four-role factor count");
        for (auto factor : factors) {
            auto once = apply_factor(identity(4), factor, 4, table);
            Factor inverse = factor;
            inverse.g += 1;
            require(apply_factor(once, inverse, 4, table) == identity(4),
                    "factor inverse");
        }

        SearchResult three_negative{}, two_negative{}, all_zi{}, mixed{};
        std::thread three([&] { three_negative = meet(3, 3, 4, "333", table); });
        std::thread two([&] { two_negative = meet(3, 3, 4, "332", table); });
        std::thread zi([&] { all_zi = meet(4, 3, 4, "3330", table); });
        std::thread zj([&] { mixed = meet(4, 3, 4, "3350", table); });
        three.join();
        two.join();
        zi.join();
        zj.join();
        const auto depth_two = depth_ball(4, 2, table);

        std::cout << "{"
                  << "\"r4_3330_hits\":" << all_zi.hits
                  << ",\"r4_3350_hits\":" << mixed.hits
                  << ",\"r4_inverse\":" << all_zi.inverse_ball
                  << ",\"r4_prefix\":" << all_zi.prefix_ball
                  << ",\"r4_candidates\":" << all_zi.candidates
                  << ",\"r4_3350_candidates\":" << mixed.candidates
                  << ",\"r3_333_hits\":" << three_negative.hits
                  << ",\"r3_332_hits\":" << two_negative.hits
                  << ",\"r3_inverse\":" << three_negative.inverse_ball
                  << ",\"factors_r4\":" << factors.size()
                  << ",\"factors_r3\":" << alphabet(3, false).size()
                  << ",\"r4_depth2\":" << depth_two
                  << "}\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << "\n";
        return 1;
    }
}
