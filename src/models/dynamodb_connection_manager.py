import boto3


class DynamoDbDatabaseManager:

    ALL_GAME_ATTRIBUTES = (
        'players', 'game_state', 'n_die', 'winning_score', 'allowed_next_turns', 'already_happened_turns', 'winner'
    )

    def __init__(self, db_name):
        dynamodb = boto3.resource('dynamodb')
        self.table = dynamodb.Table(db_name)

    def update_game(self, game_id, players, state, n_die, winning_score, allowed_next_turns, already_happened_turns, winner):
        new_item = self.table.update_item(
            Key={
                'game_id': game_id,
            },
            UpdateExpression="set players=:p, game_state=:s, n_die=:nd, winning_score=:ws, winner=:w, allowed_next_turns=:ant, already_happened_turns=:aht ",
            ExpressionAttributeValues={
                ':p': [p.to_dict() for p in players],
                ':s': state,
                ':nd': n_die,
                ':ws': winning_score,
                ':ant': {str(id): t.to_dict() for id, t in allowed_next_turns.items()},
                ':aht': [t.to_dict() for t in already_happened_turns],
                ':w': winner,
            },
            ReturnValues="UPDATED_NEW"
        )['Attributes']
        return new_item

    def get_game(self, game_id):
        entry = self.table.get_item(
            Key={
                'game_id': game_id,
            },
            AttributesToGet=self.ALL_GAME_ATTRIBUTES,
            ConsistentRead=True,
        )['Item']
        return entry
