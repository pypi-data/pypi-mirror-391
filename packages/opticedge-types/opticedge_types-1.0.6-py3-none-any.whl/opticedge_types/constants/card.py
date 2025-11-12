from opticedge_types.enums.card import CardType


CARD_COLLECTION_MAP: dict[CardType, str] = {
    CardType.POKEMON: "pokemon_cards",
    CardType.LORCANA: "lorcana_cards",
    CardType.MAGIC: "magic_cards",
    CardType.YUGIOH: "yugioh_cards",
    CardType.VIDEO_GAMES: "video_games",
}
