INF729 SPARK

TP 3 : Machine learning avec Spark

Réalisation : Anatoli de BRADKE

Remarques:
- l'attribut 'path' dans les fonctions de read et de write csv doivent être modifier avant de compiler.
- le temps d'excecution est d'environ 5/10min.

Classification:
- logistic regression donne un f1-score de 0.66 avec la grille d'hyper-paramètres suivante:
      val paramGrid = new ParamGridBuilder()
                            .addGrid(lr.regParam, Array(10e-8, 10e-6, 10e-4,10e-2))
                            .addGrid(cvModel.minDF,Array(55.0, 75.0, 95.0))
                            .build()
- RandomForestClassifier donne un f1-score de O.57 avec la grille d'hyper-paramètres suivante:
      val paramGrid = new ParamGridBuilder()
                            .addGrid(rf.numTrees, Array(100, 150, 200))
                            .addGrid(rf.maxDepth, Array(15, 20, 30))
                            .addGrid(cvModel.minDF,Array(55.0, 75.0, 95.0))
                            .build()

Bonne correction.

Anatoli de BRADKE
