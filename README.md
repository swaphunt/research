# SwapHunt Research

Data studies from [SwapHunt](https://swaphunt.dev/research). Code and data for every article.

We tested it so you don't have to. Every study folder contains the code, the processed data and the charts behind one published article, so every number can be checked and reproduced.

Analysis code written with AI assistance and reviewed by a human.

## Studies

| Study | Article | Published |
|---|---|---|
| [extreme-fear](extreme-fear/) | [https://swaphunt.dev/research/extreme-fear-bitcoin-buy-signal](https://swaphunt.dev/research/extreme-fear-bitcoin-buy-signal) | 2026-10-31 |

## Reproduce a study

Each folder has its own README. In short:

    cd <study>
    python -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    ./run_all.sh

Some studies fetch raw data from public APIs instead of shipping it. See each study's `data/SOURCES.md`.

## License

- Code: MIT (see [LICENSE](LICENSE))
- Data, charts and text: CC BY 4.0 (see [LICENSE-DATA](LICENSE-DATA))
  - Exception: studies that use Binance Vision price data (currently extreme-fear) license their derived data, charts and figures CC BY-NC-SA 4.0, non-commercial only. See the License section in each study's README.
- Fonts in `shared/fonts/`: SIL Open Font License 1.1

Please credit "SwapHunt (swaphunt.dev)".

Nothing here is investment advice.
