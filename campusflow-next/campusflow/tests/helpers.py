import copy


def make_tickets():
    """Three tickets: T001 critical Network, T002 low Hardware, T003 high Software."""
    from tickets import create_ticket
    tickets = []
    create_ticket(tickets, "Wifi down in library", "Network", "high", 15)
    create_ticket(tickets, "Projector broken", "Hardware", "low", 1)
    create_ticket(tickets, "Wifi login fails", "Software", "high", 2)
    return tickets


def snapshot(tickets):
    return copy.deepcopy(tickets)


def scripted(inputs):
    """An input() replacement that feeds `inputs` in order, then raises EOFError."""
    items = iter(inputs)

    def fake_input(prompt=""):
        try:
            return next(items)
        except StopIteration:
            raise EOFError
    return fake_input
