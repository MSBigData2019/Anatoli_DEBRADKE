package com.sparkProject

import org.apache.spark.SparkConf
import org.apache.spark.ml.Pipeline
import org.apache.spark.ml.classification.LogisticRegression
import org.apache.spark.ml.feature.{CountVectorizer, IDF, OneHotEncoder, RegexTokenizer, StopWordsRemover, StringIndexer, VectorAssembler}
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.ml.tuning.{ParamGridBuilder, TrainValidationSplit}
import org.apache.spark.ml.evaluation.{MulticlassClassificationEvaluator}
import org.apache.spark.sql.functions._


object Trainer {

  def main(args: Array[String]): Unit = {

    // Configuration pour la SparkSession
    val conf = new SparkConf().setAll(Map(
      "spark.scheduler.mode" -> "FIFO",
      "spark.speculation" -> "false",
      "spark.reducer.maxSizeInFlight" -> "48m",
      "spark.serializer" -> "org.apache.spark.serializer.KryoSerializer",
      "spark.kryoserializer.buffer.max" -> "1g",
      "spark.shuffle.file.buffer" -> "32k",
      "spark.default.parallelism" -> "12",
      "spark.sql.shuffle.partitions" -> "12",
      "spark.driver.maxResultSize" -> "2g"
    ))

    // SparkSession
    val spark = SparkSession
      .builder
      .config(conf)
      .appName("TP_spark")
      .getOrCreate()


    /** 1 - CHARGEMENT DES DONNEES
      *
      * Chargement des données préparées dans par le Preprocessor.
      *
      **/


    val df: DataFrame = spark.read.parquet("/Users/anatoli_debradke/Desktop/MS_BGD/INF729_Hadoop/Spark/TP/TP_Starter/prepared_trainingset")



    /** 2 -  TRAITEMENT DES DONNEES TEXTUELLES
      *
      * La variable 'text' n'est pas utilisable telle quelle par les algorithmes de ML
      * car ils ont besoin de données numériques.
      * On applique donc l'algorithme TF-IDF afin de convertir cette variable en donnée numérique.
      *
      **/

    // Stage 1 : Tokenizer
    val regexTokenizer = new RegexTokenizer()
      .setPattern("\\W+")
      .setGaps(true)
      .setInputCol("text")
      .setOutputCol("tokens")

    // Stage 2 : StopWordsRemover
    val remover = new StopWordsRemover()
      .setInputCol("tokens")
      .setOutputCol("filtered")

    // Stage 3 : CountVectorizer
    val cvModel = new CountVectorizer()
      .setInputCol("filtered")
      .setOutputCol("tf")

    // Stage 4: IDF
    val idf = new IDF()
      .setInputCol("tf")
      .setOutputCol("tfidf")



    /** 3 - TRAITEMENT DES DONNEES CATEGORIQUE
      *
      * On cherche à convertir les variables catégorielles ['country2','currency2]
      * en variables numériques
      *
      **/

    // Stage 5: StringIndexer  sur la variable 'country2'
    val indexerCountry = new StringIndexer()
      .setInputCol("country2")
      .setOutputCol("country_indexed")
      .setHandleInvalid("skip")

    // Stage 6: OneHotEncoder sur la variable 'country2'
    val encoderCountry = new OneHotEncoder()
      .setInputCol("country_indexed")
      .setOutputCol("country_onehot")

    // Stage 7: StringIndexer sur la variable 'currency2'
    val indexerCurrency = new StringIndexer()
      .setInputCol("currency2")
      .setOutputCol("currency_indexed")
      .setHandleInvalid("skip")

    // Stage 8: OneHotEncoder sur la variable 'currency2'
    val encoderCurrency = new OneHotEncoder()
      .setInputCol("currency_indexed")
      .setOutputCol("currency_onehot")



    /** 4 - MISE AU FORMAT SPARK.ML
      *
      * Les libraries spark.ML necessite un format de données particulier:
      * les colonnes utilisées en input des modèle (features) doivent être regroupées dans une seule colonne
      *
      **/

    // Stage 9: Création de la colonne 'features'
    val assembler = new VectorAssembler()
      .setInputCols(Array("tfidf", "days_campaign", "hours_prepa", "goal", "country_onehot", "currency_onehot"))
      .setOutputCol("features")

    // Stage 10: Classification par regression logistique
    val lr = new LogisticRegression()
      .setElasticNetParam(0.0)
      .setFitIntercept(true)
      .setFeaturesCol("features")
      .setLabelCol("final_status")
      .setStandardization(true)
      .setPredictionCol("predictions")
      .setRawPredictionCol("raw_predictions")
      .setThresholds(Array(0.7,0.3))
      .setTol(1.0e-6)
      .setMaxIter(300)

    // Création de la Pipeline
    val pipeline = new Pipeline()
      .setStages(Array(regexTokenizer,
        remover, cvModel, idf, indexerCountry,
        indexerCurrency, encoderCountry,
        encoderCurrency, assembler, lr))



    /** 5 - ENTRAINEMENT ET TUNNING DU MODELE
      *
      * Séparation des données aléatoirement en un training set (90%) et un test set (10%)
      * Puis Entrainement du classifieur et réglage des hyper-paramètres de l'algorithme
      *
      **/

    // Split des données en Training Set et Test Set
    val Array(training, test) = df
      .randomSplit(Array(0.9,0.1), seed=11L)

    // Grille de valeur des Hyper-paramètres à tester
    val paramGrid = new ParamGridBuilder()
      .addGrid(lr.regParam, Array(10e-8, 10e-6, 10e-4,10e-2))
      .addGrid(cvModel.minDF, Array(55.0, 75.0, 95.0))
      .build()

    // Evaluation par le F1 Score
    val evaluator = new MulticlassClassificationEvaluator()
      .setLabelCol("final_status")
      .setPredictionCol("predictions")
      .setMetricName("f1")

    // Choix des Hyper-paramètres optimaux
    val trainValidationSplit = new TrainValidationSplit()
      .setEstimator(pipeline)
      .setEvaluator(evaluator)
      .setEstimatorParamMaps(paramGrid)
      .setTrainRatio(0.7)

    // Application du modèle optimal sur le training set
    val validationModel = trainValidationSplit.fit(training)

    // Calcul des predictions du modèle optimal
    val dfPrediction = validationModel
      .transform(test)
      .select("features","final_status", "predictions", "raw_predictions")

    // Calcul du F1 Score
    val metrics = evaluator.evaluate(dfPrediction)
    println("F1 Score du modèle sur le Test set : " + metrics)

    // Affiche les predictions
    dfPrediction.groupBy("final_status","predictions").count.show()
  }
}
