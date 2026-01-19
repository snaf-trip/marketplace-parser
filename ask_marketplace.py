def ask_marketplace():
    print("\nС каким маркетплейсом вы будете работать?")
    print("1 — Ozon")
    print("2 — Wildberries")
    print("3 — Yandex Market")

    while True:
        choice = input("Введите номер (1/2/3): ").strip()
        if choice == "1":
            return "ozon"
        elif choice == "2":
            return "wildberries"
        elif choice == "3":
            return "yandex_market"
        else:
            print("❌ Неверный ввод. Попробуйте ещё раз.")