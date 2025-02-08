from data_selects.find import find_in_documents


def main():
    while True:
        user_input = input("What do you want to find? choose between "
                           "person or quote, exit to finish: ").lower()
        match user_input:
            case "person":
                while True:
                    person_user_input = input("you can search by name or description, "
                                              "if you want to back - just write 'back': ")
                    processed_dict = {person_user_input[0]: person_user_input[1]}
                    find_in_documents("person", processed_dict)
                    if person_user_input.lower() == "back":
                        break
            case "quote":
                while True:
                    quote_user_input = input("you can search by tags or author, "
                                             "if you want to back - just write 'back': ")
                    processed_dict = {quote_user_input[0]: quote_user_input[1]} if len(quote_user_input) == 2 \
                        else {quote_user_input[0]: quote_user_input[1:].split(",")}
                    find_in_documents("quotes", processed_dict)
                    if quote_user_input.lower() == "back":
                        break
            case "exit":
                print("See you again, goodbye!")
                break

