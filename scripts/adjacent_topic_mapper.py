# scripts/adjacent_topic_mapper.py

class AdjacentTopicMapper:

    adjacency_map = {
        "AI": ["Automation", "Economy", "Labor Markets"],
        "Automation": ["Supply Chains", "Robotics", "AI"],
        "Economy": ["Inflation", "Policy", "AI"],
        "Space": ["AI", "Defense Systems", "Energy"],
    }

    def suggest_adjacent(self, current_cluster: str):
        return self.adjacency_map.get(current_cluster, [])
