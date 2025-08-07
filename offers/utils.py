from offers.models import Offer, OfferFailed


def clean_text(element, default="NULL"):
    if element is None:
        return default
    return element.text.strip()


def filter_new_paths(paths):
    """
    Filter out paths that already exist in the database.
    :param paths: List of offer paths to filter
    :return: List of paths that do not exist in the database
    """
    existing_paths = set(Offer.objects.values_list("path", flat=True))
    return [path for path in paths if path not in existing_paths]


def save_failed_offer(offer):
    """
    Save an offer that failed to scrape to the OfferFailed model.
    :param offer: Dictionary containing offer data
    """
    OfferFailed.objects.get_or_create(
        path=offer["path"],
        defaults={"error_message": offer.get("error", "Unknown error")}
    )
    print(f"Saved failed offer: {offer['path']} with error: {offer.get('error', 'Unknown error')}")