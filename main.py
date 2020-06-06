import pandas as pd
from time import time

from hw2_comp import run_deferred_acceptance_for_pairs_comp, count_blocking_pairs_comp, calc_total_welfare_comp
from hw2_part1 import run_deferred_acceptance, run_deferred_acceptance_for_pairs, count_blocking_pairs
from hw2_part2 import run_market_clearing, calc_total_welfare


def write_matching(matching: dict, task, n):
    df = pd.DataFrame.from_dict(matching, orient='index').sort_index()
    df.to_csv(f'matching_task_{task}_data_{n}.csv', header=['pid'], index_label='sid')
    print(f'\nmatching_task_{task}_data_{n}.csv was written\n')


def write_projects_prices(prices_dict: dict, n):
    df = pd.DataFrame.from_dict(prices_dict, orient='index').sort_index()
    df.to_csv(f'mc_task_data_{n}.csv', header=['price'], index_label='pid')
    print(f'\nmc_task_data_{n}.csv was written\n')


def main(n):
    print(f'running for dataset {n}')

    matching_dict_1 = run_deferred_acceptance(n)
    write_matching(matching_dict_1, 'single', n)
    block_pairs_1 = count_blocking_pairs(f'matching_task_single_data_{n}.csv', n)
    welfare_1 = calc_total_welfare(f'matching_task_single_data_{n}.csv', n)
    print(f'Total welfare from the single matching: {welfare_1}')
    print(f'Number of blocking pairs from single matching: {block_pairs_1}')

    matching_dict_2 = run_deferred_acceptance_for_pairs(n)
    write_matching(matching_dict_2, 'coupled', n)
    block_pairs_2 = count_blocking_pairs(f'matching_task_coupled_data_{n}.csv', n)
    welfare_2 = calc_total_welfare(f'matching_task_coupled_data_{n}.csv', n)
    print(f'Total welfare from the coupled matching: {welfare_2}')
    print(f'Number of blocking pairs from coupled matching: {block_pairs_2}')

    matching_dict_3, prices_dict = run_market_clearing(n)
    write_matching(matching_dict_3, 'mcp', n)
    write_projects_prices(prices_dict, n)
    welfare_3 = calc_total_welfare(f'matching_task_mcp_data_{n}.csv', n)
    print(f'Total welfare from the MCP matching: {welfare_3}')

    matching_dict_comp = run_deferred_acceptance_for_pairs_comp(n)
    write_matching(matching_dict_comp, 'competition', n)
    block_pairs_comp = count_blocking_pairs_comp(f'matching_task_competition_data_{n}.csv', n)
    welfare_comp = calc_total_welfare_comp(f'matching_task_competition_data_{n}.csv', n)
    print(f'Total welfare from the coupled matching: {welfare_comp}')
    print(f'Number of blocking pairs from coupled matching: {block_pairs_comp}')


if __name__ == '__main__':
    x = time()
    for i in range(1, 5):
        main(i)
    #main('test')
    #main('test_mc')
    #main(1)
    print(f'Running time: {time() - x} sec')
