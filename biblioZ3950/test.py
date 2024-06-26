def search_library(host, port, database, query, syntax="USMARC"):
    conn = zoom.Connection(host, port)
    conn.databaseName = database
    conn.preferredRecordSyntax = syntax

    query = zoom.Query('CCL', query)

    try:
        res = conn.search(query)
    except zoom.QueryError as e:
        print(f"Errore nella query: {e}")
        return

    print(f"Numero di risultati: {len(res)}")

    for i, r in enumerate(res):
        print(f"\nRisultato {i+1}:")
        print(r.data)

    conn.close()

def main():
    if len(sys.argv) != 6:
        print("Uso: python script.py <host> <port> <database> <tipo_ricerca> <valore>")
        print("Tipi di ricerca supportati: author, title, isbn")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    database = sys.argv[3]
    search_type = sys.argv[4].lower()
    search_value = sys.argv[5]

    if search_type == "author":
        query = f'au="{search_value}"'
    elif search_type == "title":
        query = f'ti="{search_value}"'
    elif search_type == "isbn":
        query = f'isbn="{search_value}"'
    else:
        print("Tipo di ricerca non supportato. Usa 'author', 'title', o 'isbn'.")
        sys.exit(1)

    search_library(host, port, database, query)

if __name__ == "__main__":
    main()
