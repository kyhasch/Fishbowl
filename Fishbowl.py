import pandas as pd
import argparse
import sys

def max_bipartite_matching(adj, left, right):
    """
    adj: dict mapping each u in left to a list of v in right that u may match to
    left, right: lists of node names
    Returns dict matching u->v if perfect matching exists, else None.
    """
    # matchR[v] = the u currently matched to v, or None
    matchR = {v: None for v in right}

    def dfs(u, seen):
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                # if v is free or we can re-match the u' currently at v
                if matchR[v] is None or dfs(matchR[v], seen):
                    matchR[v] = u
                    return True
        return False

    # Try to find match for every u in left
    for u in left:
        seen = {v: False for v in right}
        if not dfs(u, seen):
            return None

    # invert the matching: u -> v
    return {matchR[v]: v for v in right if matchR[v] is not None}

def main(input_csv, output_csv=None):
    # 1) load your existing 0/1 matrix
    df = pd.read_csv(input_csv, index_col=0)
    names = list(df.index)

    # 2) build adjacency of allowed edges
    #    u->v if v != u and df[u,v]==0 (i.e. not previously assigned)
    adj = {
        giver: [recip for recip in names
                if recip != giver and df.loc[giver, recip] == 0]
        for giver in names
    }

    # 3) run bipartite matching
    matching = max_bipartite_matching(adj, names, names)
    if matching is None:
        print("No valid assignment possible under the current constraints. Exiting.")
        sys.exit(1)

    # 4) record & print
    for giver, recip in matching.items():
        df.loc[giver, recip] = 1

    print("\nAssignments:")
    for giver, recip in matching.items():
        print(f"  {giver} -> {recip}")

    # 5) output updated matrix
    if output_csv:
        df.to_csv(output_csv)
        print(f"\nUpdated matrix written to '{output_csv}'.")
    else:
        print("\nUpdated matrix:")
        print(df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Deterministically assign each person to another without repeats."
    )
    parser.add_argument("input_csv",
                        help="Path to input CSV (names×names zero/one matrix).")
    parser.add_argument("-o", "--output",
                        help="Where to save the updated CSV. If omitted, prints to stdout.")
    args = parser.parse_args()
    main(args.input_csv, args.output)
